import json
import os
from statistics import mean

import requests
from openai import OpenAI


ENV_BASE_URL = os.getenv("ENV_BASE_URL", "http://localhost:8000")
API_BASE_URL = os.getenv("API_BASE_URL")
MODEL_NAME = os.getenv("MODEL_NAME")
API_KEY = os.getenv("OPENAI_API_KEY") or os.getenv("HF_TOKEN")


def require_env(var_name: str, value: str | None):
    if not value:
        raise RuntimeError(f"Missing required environment variable: {var_name}")


def build_client() -> OpenAI:
    require_env("API_BASE_URL", API_BASE_URL)
    require_env("MODEL_NAME", MODEL_NAME)
    require_env("HF_TOKEN or OPENAI_API_KEY", API_KEY)
    return OpenAI(base_url=API_BASE_URL, api_key=API_KEY)


def call_model(client: OpenAI, system_prompt: str, user_prompt: str) -> dict:
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
    response = requests.post(f"{ENV_BASE_URL}/step", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def main():
    client = build_client()
    tasks = requests.get(f"{ENV_BASE_URL}/tasks", timeout=10).json()["tasks"]

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
        schema_context = json.dumps(task_map[prompt["task_name"]], indent=2)
        action = call_model(
            client=client,
            system_prompt=system_prompt,
            user_prompt=f"{prompt['user_prompt']}\n\nTask metadata:\n{schema_context}",
        )
        result = run_step(action)
        scores[prompt["grader_key"]] = result["reward"]
        print(f"{prompt['grader_key']}: {result['reward']}")

    scores["average"] = round(mean(scores.values()), 2)
    print(f"average: {scores['average']}")


if __name__ == "__main__":
    main()
