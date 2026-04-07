import json
import os
import sys
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
    timestamp = datetime.now().isoformat()
    print(f"[START] {json.dumps({'task': task_name, 'timestamp': timestamp})}", flush=True)


def log_step(action: dict, observation: dict, reward: float, done: bool):
    print(f"[STEP] {json.dumps({'action': action, 'reward': reward, 'done': done})}", flush=True)


def log_end(task_name: str, score: float):
    timestamp = datetime.now().isoformat()
    print(f"[END] {json.dumps({'task': task_name, 'score': score, 'timestamp': timestamp})}", flush=True)


def wait_for_server(max_attempts=30, delay=2):
    """Wait for the environment server to be ready."""
    print(f"Waiting for environment server at {ENV_BASE_URL}...", flush=True, file=sys.stderr)
    for attempt in range(max_attempts):
        try:
            response = requests.get(f"{ENV_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print(f"Server ready after {attempt + 1} attempts", flush=True, file=sys.stderr)
                return True
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            if attempt < max_attempts - 1:
                print(f"Waiting for server... (attempt {attempt + 1}/{max_attempts})", flush=True, file=sys.stderr)
                time.sleep(delay)
            else:
                print(f"Server not available after {max_attempts} attempts", flush=True, file=sys.stderr)
                return False
        except Exception as e:
            print(f"Unexpected error checking server: {e}", flush=True, file=sys.stderr)
            return False
    return False


def build_client() -> OpenAI:
    if not API_KEY:
        print("WARNING: No API key found, using mock client", flush=True, file=sys.stderr)
        return None
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def call_model(client: OpenAI, system_prompt: str, user_prompt: str) -> dict:
    if client is None:
        return {"task": "mock_task"}
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
        print(f"Error calling model: {e}", flush=True, file=sys.stderr)
        raise


def run_step(payload: dict) -> dict:
    try:
        response = requests.post(f"{ENV_BASE_URL}/step", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error calling /step endpoint: {e}", flush=True, file=sys.stderr)
        raise


def main():
    try:
        # Wait for server to be ready
        if not wait_for_server():
            print("ERROR: Environment server is not available", flush=True, file=sys.stderr)
            print("ERROR: Make sure the server is running on the expected port", flush=True, file=sys.stderr)
            sys.exit(1)
        
        # Get tasks with error handling
        try:
            tasks_response = requests.get(f"{ENV_BASE_URL}/tasks", timeout=10)
            tasks_response.raise_for_status()
            tasks = tasks_response.json()["tasks"]
            print(f"Loaded {len(tasks)} tasks", flush=True, file=sys.stderr)
        except Exception as e:
            print(f"Error fetching tasks: {e}", flush=True, file=sys.stderr)
            sys.exit(1)

        # Use baseline approach - direct API calls without LLM
        scores = {}
        
        # Task 1: find_scholarships
        task_name = "find_scholarships"
        log_start(task_name)
        try:
            action = {
                "task": "find_scholarships",
                "name": "Asha",
                "gender": "Female",
                "category": "General",
                "state": "Delhi",
                "marks_class10": 92.0,
                "marks_class12": 91.0,
                "annual_income": 200000,
                "course_level": "Undergraduate",
                "course_name": "B.Tech",
                "age": 18
            }
            
            result = run_step(action)
            observation = result.get("observation", {})
            reward = result["reward"]
            done = result.get("done", True)
            
            log_step(action, observation, reward, done)
            scores["task1"] = reward
            log_end(task_name, reward)
        except Exception as e:
            print(f"Error processing task {task_name}: {e}", flush=True, file=sys.stderr)
            scores["task1"] = 0.0
            log_end(task_name, 0.0)

        # Task 2: find_exams
        task_name = "find_exams"
        log_start(task_name)
        try:
            action = {
                "task": "find_exams",
                "name": "Rohan",
                "gender": "Male",
                "category": "General",
                "state": "Delhi",
                "marks_class10": 86.0,
                "marks_class12": 84.0,
                "annual_income": 300000,
                "course_level": "Graduation",
                "course_name": "B.Com",
                "age": 22
            }
            
            result = run_step(action)
            observation = result.get("observation", {})
            reward = result["reward"]
            done = result.get("done", True)
            
            log_step(action, observation, reward, done)
            scores["task2"] = reward
            log_end(task_name, reward)
        except Exception as e:
            print(f"Error processing task {task_name}: {e}", flush=True, file=sys.stderr)
            scores["task2"] = 0.0
            log_end(task_name, 0.0)

        # Task 3: check_eligibility
        task_name = "check_eligibility"
        log_start(task_name)
        try:
            action = {
                "task": "check_eligibility",
                "student": {
                    "name": "Riya",
                    "gender": "Female",
                    "category": "General",
                    "state": "Delhi",
                    "marks_class10": 92.0,
                    "marks_class12": 92.0,
                    "annual_income": 100000,
                    "course_level": "Undergraduate",
                    "course_name": "B.Tech",
                    "age": 21
                },
                "scholarship_name": "JN Tata Endowment Loan Scholarship 2026-27"
            }
            
            result = run_step(action)
            observation = result.get("observation", {})
            reward = result["reward"]
            done = result.get("done", True)
            
            log_step(action, observation, reward, done)
            scores["task3"] = reward
            log_end(task_name, reward)
        except Exception as e:
            print(f"Error processing task {task_name}: {e}", flush=True, file=sys.stderr)
            scores["task3"] = 0.0
            log_end(task_name, 0.0)

        scores["average"] = round(mean(scores.values()), 2)
        print(f"\n{'='*50}", flush=True, file=sys.stderr)
        print(f"FINAL RESULTS", flush=True, file=sys.stderr)
        print(f"{'='*50}", flush=True, file=sys.stderr)
        print(f"Task 1 (Scholarship Finder): {scores['task1']}", flush=True, file=sys.stderr)
        print(f"Task 2 (Exam Finder): {scores['task2']}", flush=True, file=sys.stderr)
        print(f"Task 3 (Eligibility Check): {scores['task3']}", flush=True, file=sys.stderr)
        print(f"Average Score: {scores['average']}", flush=True, file=sys.stderr)
        print(f"{'='*50}", flush=True, file=sys.stderr)
        
    except Exception as e:
        print(f"FATAL ERROR: {e}", flush=True, file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
