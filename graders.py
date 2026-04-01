from environment import ScholarshipEnvironment
from models import EligibilityAction, StudentAction


def _score_presence(items: list[str], expected: list[str], forbidden: list[str]) -> float:
    if not items:
        return 0.0

    expected_hits = sum(1 for name in expected if name in items)
    forbidden_hits = sum(1 for name in forbidden if name in items)

    expected_score = expected_hits / len(expected) if expected else 1.0
    penalty = forbidden_hits / len(forbidden) if forbidden else 0.0
    return max(0.0, min(1.0, expected_score - penalty))


def grade_task1() -> float:
    env = ScholarshipEnvironment()
    student = StudentAction(
        name="Asha",
        gender="Female",
        category="General",
        state="Delhi",
        marks_class10=92,
        marks_class12=91,
        annual_income=200000,
        course_level="Undergraduate",
        course_name="B.Tech",
        age=18,
        year_of_study=1,
        task="find_scholarships",
    )
    result = env.step(student)
    scholarship_names = [item.name for item in result.observation.matched_scholarships]
    ranking_bonus = 1.0 if scholarship_names[:1] and scholarship_names[0] == "Vivo KanyaGyaan Scholarship Program 2025-26" else 0.7
    presence_score = _score_presence(
        items=scholarship_names,
        expected=[
            "Vivo KanyaGyaan Scholarship Program 2025-26",
            "Buddy4Study ICICI Bank Domestic Education Loan Programme",
        ],
        forbidden=["JN Tata Endowment Loan Scholarship 2026-27"],
    )
    return round(min(1.0, 0.7 * presence_score + 0.3 * ranking_bonus), 2)


def grade_task2() -> float:
    env = ScholarshipEnvironment()
    student = StudentAction(
        name="Rohan",
        gender="Male",
        category="General",
        state="Delhi",
        marks_class10=86,
        marks_class12=84,
        annual_income=300000,
        course_level="Graduation",
        course_name="B.Com",
        age=22,
        task="find_exams",
    )
    result = env.step(student)
    exam_names = [item.name for item in result.observation.matched_exams]
    presence_score = _score_presence(
        items=exam_names,
        expected=["IBPS Clerk 2025", "SBI PO 2025", "SSC CGL 2025"],
        forbidden=["GATE 2026"],
    )
    ranking_bonus = 1.0 if "GATE 2026" not in exam_names[:5] else 0.0
    return round(min(1.0, 0.8 * presence_score + 0.2 * ranking_bonus), 2)


def grade_task3() -> float:
    env = ScholarshipEnvironment()
    student = StudentAction(
        name="Riya",
        gender="Female",
        category="General",
        state="Delhi",
        marks_class10=92,
        marks_class12=92,
        annual_income=100000,
        course_level="Undergraduate",
        course_name="B.Tech",
        age=21,
        task="find_scholarships",
    )
    action = EligibilityAction(
        student=student,
        scholarship_name="JN Tata Endowment Loan Scholarship 2026-27",
    )
    result = env.step(action).observation

    failed_course_level = any("Course level" in item for item in result.failed_criteria)
    not_eligible = not result.is_eligible
    no_false_positive = result.eligibility_score < 1.0

    score = 0.0
    score += 0.4 if not_eligible else 0.0
    score += 0.4 if failed_course_level else 0.0
    score += 0.2 if no_false_positive else 0.0
    return round(score, 2)


def grade_all_tasks() -> dict[str, float]:
    task1 = grade_task1()
    task2 = grade_task2()
    task3 = grade_task3()
    average = round((task1 + task2 + task3) / 3, 2)
    return {"task1": task1, "task2": task2, "task3": task3, "average": average}
