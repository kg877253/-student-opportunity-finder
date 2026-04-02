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
    """
    Hard task: Requires nested reasoning about eligibility.
    Agent must understand:
    1. Basic eligibility (age, income, marks)
    2. Course compatibility 
    3. Study location constraints
    4. Qualification level matching
    5. Reason about why student is/isn't eligible
    """
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
        task="check_eligibility",
    )
    
    # Test 1: Overseas postgrad scholarship (should fail - undergrad student)
    action1 = EligibilityAction(
        student=student,
        scholarship_name="JN Tata Endowment Loan Scholarship 2026-27",
        task="check_eligibility"
    )
    result1 = env.step(action1)
    obs1 = result1.observation
    
    # Should correctly identify course level mismatch
    course_level_check = any("Post Graduate" in str(c) or "postgraduate" in str(c).lower() 
                             for c in obs1.failed_criteria)
    
    # Test 2: Women tech scholarship (should pass - female, B.Tech, good marks)
    student2 = StudentAction(
        name="Priya",
        gender="Female",
        category="General",
        state="Maharashtra",
        marks_class10=88,
        marks_class12=87,
        annual_income=400000,
        course_level="Undergraduate",
        course_name="B.Tech",
        age=19,
        year_of_study=2,
        task="check_eligibility",
    )
    action2 = EligibilityAction(
        student=student2,
        scholarship_name="Google India Women in Engineering Scholarship 2025-26",
        task="check_eligibility"
    )
    result2 = env.step(action2)
    obs2 = result2.observation
    
    # Should identify as eligible
    should_be_eligible = obs2.is_eligible and obs2.eligibility_score >= 0.8
    
    # Test 3: Complex multi-criteria scholarship
    student3 = StudentAction(
        name="Aarav",
        gender="Male",
        category="SC",
        state="Delhi",
        marks_class10=76,
        marks_class12=78,
        annual_income=220000,
        course_level="Undergraduate",
        course_name="B.Tech",
        age=20,
        task="check_eligibility",
    )
    action3 = EligibilityAction(
        student=student3,
        scholarship_name="Infosys Foundation SC ST Technology Scholarship 2025-26",
        task="check_eligibility"
    )
    result3 = env.step(action3)
    obs3 = result3.observation
    
    # Should identify marks slightly below cutoff (needs 75%, has 78% - should pass)
    marks_reasoning = obs3.is_eligible
    
    # Scoring based on reasoning quality
    reasoning_score = 0.0
    reasoning_score += 0.35 if course_level_check else 0.0  # Identified level mismatch
    reasoning_score += 0.35 if should_be_eligible else 0.0   # Correct positive case
    reasoning_score += 0.30 if marks_reasoning else 0.0      # Edge case handling
    
    return round(min(1.0, reasoning_score), 2)


def grade_all_tasks() -> dict[str, float]:
    task1 = grade_task1()
    task2 = grade_task2()
    task3 = grade_task3()
    average = round((task1 + task2 + task3) / 3, 2)
    return {"task1": task1, "task2": task2, "task3": task3, "average": average}
