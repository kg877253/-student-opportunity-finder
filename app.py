from pathlib import Path
from uuid import uuid4

from fastapi import Cookie, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from environment import ScholarshipEnvironment
from graders import grade_all_tasks, grade_task1, grade_task2, grade_task3
from models import EligibilityAction, EnvironmentAction, FeedbackAction
from multiturn_environment import MultiTurnScholarshipGuidanceEnvironment, TASK_LIBRARY
from multiturn_graders import grade_all_multiturn_tasks, grade_easy_task, grade_hard_task, grade_medium_task
from multiturn_models import MultiTurnAction, ResetRequest

app = FastAPI(
    title="Student Opportunity Finder",
    description="A real-world OpenEnv environment for scholarship discovery, exam discovery, and eligibility analysis.",
    version="0.3.0",
)

# Add CORS so UI works from any browser or device
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "index.html"
SESSION_COOKIE = "student_opportunity_session"
env_store: dict[str, ScholarshipEnvironment] = {}
multiturn_env_store: dict[str, MultiTurnScholarshipGuidanceEnvironment] = {}


def get_or_create_env(response: Response, session_id: str | None) -> ScholarshipEnvironment:
    current_session_id = session_id or str(uuid4())
    response.set_cookie(SESSION_COOKIE, current_session_id, httponly=True, samesite="lax")
    if current_session_id not in env_store:
        env_store[current_session_id] = ScholarshipEnvironment()
    return env_store[current_session_id]


def get_or_create_multiturn_env(
    response: Response,
    session_id: str | None,
) -> MultiTurnScholarshipGuidanceEnvironment:
    current_session_id = session_id or str(uuid4())
    response.set_cookie(SESSION_COOKIE, current_session_id, httponly=True, samesite="lax")
    if current_session_id not in multiturn_env_store:
        multiturn_env_store[current_session_id] = MultiTurnScholarshipGuidanceEnvironment()
    return multiturn_env_store[current_session_id]


def get_index_html() -> HTMLResponse:
    if INDEX_FILE.exists():
        return HTMLResponse(INDEX_FILE.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Student Opportunity Finder</h1><p>Visit <a href='/docs'>/docs</a> to use the API.</p>")


@app.get("/", response_class=HTMLResponse)
def home():
    return get_index_html()


@app.get("/ui", response_class=HTMLResponse)
def ui():
    return get_index_html()


@app.get("/health")
def health():
    return {"status": "healthy", "multi_turn_rl": "available"}


@app.post("/reset")
def reset(response: Response, session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    env = get_or_create_env(response, session_id)
    return env.reset()


@app.post("/step")
def step(
    action: EnvironmentAction,
    response: Response,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    env = get_or_create_env(response, session_id)
    return env.step(action)


@app.post("/step/eligibility")
def step_eligibility(
    action: EligibilityAction,
    response: Response,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    env = get_or_create_env(response, session_id)
    return env.step(action)


@app.get("/state")
def get_state(response: Response, session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    env = get_or_create_env(response, session_id)
    return env.state_snapshot()


@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {
                "name": "find_scholarships",
                "difficulty": "easy",
                "goal": "Return high-quality scholarship recommendations for a student profile.",
                "step_action": {
                    "task": "find_scholarships",
                    "student_fields": [
                        "name", "gender", "category", "state",
                        "marks_class10", "marks_class12", "annual_income",
                        "course_level", "course_name", "age",
                    ],
                    "optional_fields": [
                        "current_marks", "previous_marks", "undergraduate_marks",
                        "year_of_study", "attendance_percentage", "study_location",
                        "domicile_state", "college_type",
                    ],
                },
            },
            {
                "name": "find_exams",
                "difficulty": "medium",
                "goal": "Return government or entrance exams that fit the student profile.",
                "step_action": {
                    "task": "find_exams",
                    "student_fields": [
                        "name", "gender", "category", "state",
                        "marks_class10", "marks_class12", "annual_income",
                        "course_level", "course_name", "age",
                    ],
                },
            },
            {
                "name": "check_eligibility",
                "difficulty": "hard",
                "goal": "Evaluate a student against a specific scholarship and explain pass, fail, and missing criteria.",
                "step_action": {
                    "task": "check_eligibility",
                    "student": "Student profile object",
                    "scholarship_name": "Exact scholarship title",
                },
            },
        ]
    }


@app.get("/baseline")
def baseline():
    scores = grade_all_tasks()
    return {
        "task1_scholarship_finder": scores["task1"],
        "task2_exam_finder": scores["task2"],
        "task3_eligibility_checker": scores["task3"],
        "average_score": scores["average"],
        "status": "All tasks are responding correctly.",
    }


@app.get("/grader")
def grader():
    return {
        "grader_scores": {
            "task1": grade_task1(),
            "task2": grade_task2(),
            "task3": grade_task3(),
        }
    }


@app.post("/feedback")
def feedback(
    data: FeedbackAction,
    response: Response,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    env = get_or_create_env(response, session_id)
    env.update_weights(data.reward, data.focus_area)
    return {"message": "Learning updated successfully", "weights": env.weights}


@app.post("/rl/reset")
def rl_reset(
    request: ResetRequest,
    response: Response,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    env = get_or_create_multiturn_env(response, session_id)
    return env.reset(request.task_name)


@app.post("/rl/step")
def rl_step(
    action: MultiTurnAction,
    response: Response,
    session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE),
):
    env = get_or_create_multiturn_env(response, session_id)
    return env.step(action)


@app.get("/rl/state")
def rl_state(response: Response, session_id: str | None = Cookie(default=None, alias=SESSION_COOKIE)):
    env = get_or_create_multiturn_env(response, session_id)
    return env.state_snapshot()


@app.get("/rl/tasks")
def rl_tasks():
    return {
        "environment_name": "multi-turn scholarship guidance RL environment",
        "tasks": [
            {
                "name": task_name,
                "difficulty": config["difficulty"],
                "guidance_mode": config["guidance_mode"],
                "goal": config["goal"],
                "max_steps": config["max_steps"],
                "initial_hidden_fields": [
                    field for field in config["student_profile"]
                    if field not in config["initial_revealed_fields"] and field != "name"
                ],
                "critical_fields": config["critical_fields"],
            }
            for task_name, config in TASK_LIBRARY.items()
        ],
    }


@app.get("/rl/baseline")
def rl_baseline():
    scores = grade_all_multiturn_tasks()
    return {
        "easy_task": scores["easy"],
        "medium_task": scores["medium"],
        "hard_task": scores["hard"],
        "average_score": scores["average"],
        "status": "Reference multi-turn baseline completed.",
    }


@app.get("/rl/grader")
def rl_grader():
    return {
        "grader_scores": {
            "easy_scholarship_shortlist": grade_easy_task(),
            "medium_exam_guidance": grade_medium_task(),
            "hard_mixed_guidance": grade_hard_task(),
        }
    }