import json
import os
import time
from datetime import datetime
from statistics import mean

import requests
from openai import OpenAI


ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4")
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")


def log_start(task_name: str):
    timestamp = datetime.utcnow().isoformat()
    print(f"[START] {json.dumps({'task': task_name, 'timestamp': timestamp})}")


def log_step(action: dict, observation: dict, reward: float, done: bool):
    print(f"[STEP] {json.dumps({'action': action, 'reward': reward, 'done': done})}")


def log_end(task_name: str, score: float):
    timestamp = datetime.utcnow().isoformat()
    print(f"[END] {json.dumps({'task': task_name, 'score': score, 'timestamp': timestamp})}")


def require_env(var_name: str, value: str | None):
    if not value:
        raise RuntimeError(f"Missing required environment variable: {var_name}")


def wait_for_server(max_attempts=30, delay=2):
    """Wait for the environment server to be ready."""
    print(f"Waiting for environment server at {ENV_BASE_URL}...")
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{ENV_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print(f"✓ Server ready after {attempt + 1} attempts")
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt < max_attempts - 1:
                print(f"Waiting for server... (attempt {attempt + 1}/{max_attempts})")
                time.sleep(delay)
            else:
                print(f"✗ Server not available after {max_attempts} attempts")
                return False
        except Exception as e:
            print(f"Unexpected error checking server: {e}")
            return False
    return False


def build_client() -> OpenAI:
    require_env("API_BASE_URL", API_BASE_URL)
    require_env("MODEL_NAME", MODEL_NAME)
    require_env("HF_TOKEN or OPENAI_API_KEY", API_KEY)
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def call_model(client: OpenAI, system_prompt: str, user_prompt: str) -> dict:
    try:
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
    except Exception as e:
        print(f"Error calling model: {e}")
        raise


def run_step(payload: dict) -> dict:
    try:
        response = requests.post(f"{ENV_BASE_URL}/step", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling /step endpoint: {e}")
        raise


def main():
    try:
        # Wait for server to be ready
        if not wait_for_server():
            print("ERROR: Environment server is not available")
            print("Make sure the server is running on the expected port")
            return
        
        client = build_client()
        
        # Get tasks with error handling
        try:
            tasks_response = requests.get(f"{ENV_BASE_URL}/tasks", timeout=10)
            tasks_response.raise_for_status()
            tasks = tasks_response.json()["tasks"]
        except Exception as e:
            print(f"Error fetching tasks: {e}")
            raise

        system_prompt = (
            "You are an agent operating an OpenEnv environment. "
            "Return only valid JSON that matches the requested task action schema."
        )

        prompts = [
            {
                "task_name": "find_scholarships",
                "grader_key": "task1",
                "user_prompt": (
                    "Generate the best action JSON for the find_scholarships task.\n"
                    "Student profile: Asha, female, general category, Delhi, Class 10 = 92, "
                    "Class 12 = 91, annual income = 200000, undergraduate first year, B.Tech, age 18.\n"
                    "Include optional fields if they improve recommendation quality."
                ),
            },
            {
                "task_name": "find_exams",
                "grader_key": "task2",
                "user_prompt": (
                    "Generate the best action JSON for the find_exams task.\n"
                    "Student profile: Rohan, male, general category, Delhi, Class 10 = 86, "
                    "Class 12 = 84, annual income = 300000, graduation, B.Com, age 22."
                ),
            },
            {
                "task_name": "check_eligibility",
                "grader_key": "task3",
                "user_prompt": (
                    "Generate the best action JSON for the check_eligibility task.\n"
                    "Student profile: Riya, female, general category, Delhi, Class 10 = 92, "
                    "Class 12 = 92, annual income = 100000, undergraduate, B.Tech, age 21.\n"
                    "Scholarship to check: JN Tata Endowment Loan Scholarship 2026-27."
                ),
            },
        ]

        task_map = {task["name"]: task for task in tasks}
        scores = {}

        for prompt in prompts:
            task_name = prompt["task_name"]
            log_start(task_name)
            
            try:
                schema_context = json.dumps(task_map[task_name], indent=2)
                action = call_model(
                    client=client,
                    system_prompt=system_prompt,
                    user_prompt=f"{prompt['user_prompt']}\n\nTask metadata:\n{schema_context}",
                )
                
                result = run_step(action)
                observation = result.get("observation", {})
                reward = result["reward"]
                done = result.get("done", True)
                
                log_step(action, observation, reward, done)
                scores[prompt["grader_key"]] = reward
                log_end(task_name, reward)
            except Exception as e:
                print(f"Error processing task {task_name}: {e}")
                scores[prompt["grader_key"]] = 0.0
                log_end(task_name, 0.0)

        scores["average"] = round(mean(scores.values()), 2)
        print(f"\n{'='*50}")
        print(f"FINAL RESULTS")
        print(f"{'='*50}")
        print(f"Task 1 (Scholarship Finder): {scores['task1']}")
        print(f"Task 2 (Exam Finder): {scores['task2']}")
        print(f"Task 3 (Eligibility Check): {scores['task3']}")
        print(f"Average Score: {scores['average']}")
        print(f"{'='*50}")
        
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
