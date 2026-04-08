import json
import os
import sys
import time
from datetime import datetime
from statistics import mean

import requests
from openai import OpenAI


# Environment variables per checklist requirements
ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")  # Default required
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")  # Default required
API_KEY = os.environ.get("API_KEY") or os.environ.get("HF_TOKEN")  # NO default


def log_start(task_name: str):
    timestamp = datetime.now().isoformat()
    print(f"[START] {json.dumps({'task': task_name, 'timestamp': timestamp})}", flush=True)


def log_step(action: dict, observation: dict, reward: float, done: bool):
    print(f"[STEP] {json.dumps({'action': action, 'reward': reward, 'done': done})}", flush=True)


def log_end(task_name: str, score: float):
    timestamp = datetime.now().isoformat()
    print(f"[END] {json.dumps({'task': task_name, 'score': score, 'timestamp': timestamp})}", flush=True)


def wait_for_server(max_attempts=60, delay=2):
    """Wait for environment server with extended timeout."""
    print(f"Waiting for server at {ENV_BASE_URL}...", flush=True, file=sys.stderr)
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{ENV_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print(f"Server ready after {attempt + 1} attempts", flush=True, file=sys.stderr)
                return True
        except:
            pass
        if attempt < max_attempts - 1:
            time.sleep(delay)
        else:
            print(f"Server still not ready after {max_attempts} attempts ({max_attempts * delay}s)", flush=True, file=sys.stderr)
    return False


def call_llm(client: OpenAI, task_name: str, task_info: dict) -> dict:
    """Call LLM through their proxy to generate action."""
    prompts = {
        "find_scholarships": {
            "profile": "Asha, female, General category, Delhi, Class 10=92%, Class 12=91%, income=200000, Undergraduate B.Tech, age 18",
            "instruction": "Return JSON with: task, name, gender, category, state, marks_class10, marks_class12, annual_income, course_level, course_name, age"
        },
        "find_exams": {
            "profile": "Rohan, male, General category, Delhi, Class 10=86%, Class 12=84%, income=300000, Graduation B.Com, age 22",
            "instruction": "Return JSON with: task, name, gender, category, state, marks_class10, marks_class12, annual_income, course_level, course_name, age"
        },
        "check_eligibility": {
            "profile": "Riya, female, General category, Delhi, Class 10=92%, Class 12=92%, income=100000, Undergraduate B.Tech, age 21. Check: JN Tata Endowment Loan Scholarship 2026-27",
            "instruction": "Return JSON with: task, student (nested object with profile fields), scholarship_name"
        }
    }
    
    prompt_data = prompts[task_name]
    
    system_prompt = (
        "You are an AI agent for an OpenEnv scholarship/exam finder environment. "
        "Generate valid JSON action for the given task. Only return the JSON object, nothing else."
    )
    
    user_prompt = f"""Task: {task_name}
Student profile: {prompt_data['profile']}
{prompt_data['instruction']}
Task schema: {json.dumps(task_info, indent=2)}"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )
    
    content = response.choices[0].message.content
    return json.loads(content)


def run_step(payload: dict) -> dict:
    """Call environment step endpoint."""
    response = requests.post(f"{ENV_BASE_URL}/step", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    # Validate API_KEY (no default per checklist)
    if not API_KEY:
        print("ERROR: API_KEY or HF_TOKEN not set", flush=True, file=sys.stderr)
        sys.exit(1)
    
    print(f"Using LLM at: {API_BASE_URL}", flush=True, file=sys.stderr)
    print(f"Using model: {MODEL_NAME}", flush=True, file=sys.stderr)
    
    # Initialize OpenAI client
    client = OpenAI(base_url=API_BASE_URL, api_key=API_KEY)
    
    # Wait for environment server with retry
    server_ready = wait_for_server()
    if not server_ready:
        # Try one more time after extra delay
        print("Retrying server connection after 10s...", flush=True, file=sys.stderr)
        time.sleep(10)
        server_ready = wait_for_server(max_attempts=30, delay=2)
        
    if not server_ready:
        print("FATAL: Cannot connect to environment server", flush=True, file=sys.stderr)
        sys.exit(1)
    
    # Get tasks from environment with retry
    task_map = {}
    for attempt in range(3):
        try:
            tasks_response = requests.get(f"{ENV_BASE_URL}/tasks", timeout=15)
            tasks_response.raise_for_status()
            tasks = tasks_response.json()["tasks"]
            task_map = {t["name"]: t for t in tasks}
            print(f"Loaded {len(tasks)} tasks", flush=True, file=sys.stderr)
            break
        except Exception as e:
            print(f"Attempt {attempt + 1}/3 fetching tasks: {e}", flush=True, file=sys.stderr)
            if attempt < 2:
                time.sleep(5)
            else:
                print(f"FATAL: Cannot fetch tasks", flush=True, file=sys.stderr)
                sys.exit(1)

    scores = {}
    task_order = [
        ("find_scholarships", "task1"),
        ("find_exams", "task2"),
        ("check_eligibility", "task3"),
    ]
    
    for task_name, grader_key in task_order:
        log_start(task_name)
        
        try:
            # Call LLM through their proxy (REQUIRED!)
            print(f"Calling LLM for {task_name}...", flush=True, file=sys.stderr)
            action = call_llm(client, task_name, task_map[task_name])
            
            # Ensure task field is set
            if "task" not in action:
                action["task"] = task_name
            
            # Call environment
            result = run_step(action)
            observation = result.get("observation", {})
            reward = result["reward"]
            done = result.get("done", True)
            
            log_step(action, observation, reward, done)
            scores[grader_key] = reward
            log_end(task_name, reward)
            print(f"{task_name}: {reward}", flush=True, file=sys.stderr)
            
        except Exception as e:
            print(f"ERROR in {task_name}: {e}", flush=True, file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
            scores[grader_key] = 0.0
            log_step({}, {}, 0.0, True)
            log_end(task_name, 0.0)

    # Summary
    avg = round(mean(scores.values()), 2)
    print(f"\nFINAL: {scores}, avg={avg}", flush=True, file=sys.stderr)


if __name__ == "__main__":
    main()
