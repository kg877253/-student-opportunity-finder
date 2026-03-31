from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from models import StudentAction, EligibilityAction
from environment import ScholarshipEnvironment
from graders import grade_task1, grade_task2, grade_task3
import os

app = FastAPI(
    title="Student Opportunity Finder",
    description="An RL environment for finding scholarships and exams for Indian students",
    version="0.1.0"
)

env = ScholarshipEnvironment()


@app.get("/", response_class=HTMLResponse)
def home():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return HTMLResponse("""
        <h1>Student Opportunity Finder</h1>
        <p>Visit <a href='/docs'>/docs</a> to use the API</p>
        """)


@app.get("/ui", response_class=HTMLResponse)
def ui():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return HTMLResponse("<h1>UI file not found!</h1>")


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/reset")
def reset():
    state = env.reset()
    return state


@app.post("/step")
def step(action: StudentAction):
    result = env.step(action)
    return result


@app.post("/step/eligibility")
def step_eligibility(action: EligibilityAction):
    result = env.step(action)
    return result


@app.get("/state")
def get_state():
    return env.state


@app.get("/tasks")
def get_tasks():
    return {
        "tasks": [
            {
                "name": "find_scholarships",
                "description": "Find matching scholarships based on student profile",
                "difficulty": "easy",
                "action_schema": {
                    "name": "string",
                    "gender": "Male or Female",
                    "category": "General, OBC, SC, ST or Minority",
                    "state": "State name like Delhi",
                    "marks_class10": "float percentage",
                    "marks_class12": "float percentage",
                    "annual_income": "float in rupees",
                    "course_level": "Undergraduate or Postgraduate",
                    "course_name": "like B.Sc or B.Tech",
                    "age": "integer",
                    "task": "find_scholarships"
                }
            },
            {
                "name": "find_exams",
                "description": "Find government exams student can apply for",
                "difficulty": "medium",
                "action_schema": {
                    "name": "string",
                    "gender": "Male or Female",
                    "category": "General, OBC, SC, ST or Minority",
                    "state": "State name like Delhi",
                    "marks_class10": "float percentage",
                    "marks_class12": "float percentage",
                    "annual_income": "float in rupees",
                    "course_level": "Undergraduate or Postgraduate",
                    "course_name": "like B.Sc or B.Tech",
                    "age": "integer",
                    "task": "find_exams"
                }
            },
            {
                "name": "check_eligibility",
                "description": "Check detailed eligibility for a specific scholarship",
                "difficulty": "hard",
                "action_schema": {
                    "student": "StudentAction object",
                    "scholarship_name": "exact scholarship name string"
                }
            }
        ]
    }


@app.get("/baseline")
def baseline():
    test_student = {
        "name": "Test Student",
        "gender": "Male",
        "category": "General",
        "state": "Delhi",
        "marks_class10": 85.0,
        "marks_class12": 82.0,
        "annual_income": 250000,
        "course_level": "Undergraduate",
        "course_name": "B.Sc",
        "age": 18,
        "task": "find_scholarships"
    }

    score1 = grade_task1(test_student)
    score2 = grade_task2(test_student)
    score3 = grade_task3(
        test_student,
        "Buddy4Study ICICI Bank Domestic Education Loan Programme"
    )
    average = round((score1 + score2 + score3) / 3, 2)

    return {
        "task1_scholarship_finder": score1,
        "task2_exam_finder": score2,
        "task3_eligibility_checker": score3,
        "average_score": average,
        "status": "All tasks working correctly!"
    }


@app.get("/grader")
def grader():
    test_student = {
        "name": "Test Student",
        "gender": "Male",
        "category": "General",
        "state": "Delhi",
        "marks_class10": 85.0,
        "marks_class12": 82.0,
        "annual_income": 250000,
        "course_level": "Undergraduate",
        "course_name": "B.Sc",
        "age": 18,
        "task": "find_scholarships"
    }

    return {
        "grader_scores": {
            "task1": grade_task1(test_student),
            "task2": grade_task2(test_student),
            "task3": grade_task3(
                test_student,
                "Buddy4Study ICICI Bank Domestic Education Loan Programme"
            )
        }
    }
@app.post("/feedback")
def feedback(data: dict):
    env.update_weights(data["reward"])
    return {"message": "Learning updated successfully"}