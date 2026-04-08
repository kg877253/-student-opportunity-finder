from environment import ScholarshipEnvironment
from models import EligibilityAction, StudentAction


def _ensure_valid_score(score: float) -> float:
    """CRITICAL: Ensure score is strictly between 0 and 1 (exclusive).
    This is a safety wrapper that guarantees no score can ever be 0.0 or 1.0."""
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return round(score, 2)


def _score_presence(items: list[str], expected: list[str], forbidden: list[str]) -> float:
    if not items:
        return 0.01  # Changed from 0.0 to satisfy (0,1) constraint

    expected_hits = sum(1 for name in expected if name in items)
    forbidden_hits = sum(1 for name in forbidden if name in items)

    expected_score = max(0.01, expected_hits / len(expected)) if expected else 0.99  # Clamp to avoid 0.0
    penalty = (forbidden_hits / len(forbidden)) if forbidden else 0.0  # Penalty can be 0, that's fine
    raw_score = expected_score - penalty
    # Clamp to (0.01, 0.99) instead of (0, 1)
    return max(0.01, min(0.99, raw_score))


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
    ranking_bonus = 0.99 if scholarship_names[:1] and scholarship_names[0] == "Vivo KanyaGyaan Scholarship Program 2025-26" else 0.7
    presence_score = _score_presence(
        items=scholarship_names,
        expected=[
            "Vivo KanyaGyaan Scholarship Program 2025-26",
            "Buddy4Study ICICI Bank Domestic Education Loan Programme",
        ],
        forbidden=["JN Tata Endowment Loan Scholarship 2026-27"],
    )
    raw_score = 0.7 * presence_score + 0.3 * ranking_bonus
    return _ensure_valid_score(raw_score)


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
    ranking_bonus = 0.99 if "GATE 2026" not in exam_names[:5] else 0.01
    raw_score = 0.8 * presence_score + 0.2 * ranking_bonus
    return _ensure_valid_score(raw_score)


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
    
    # Create student profile WITHOUT task field (not allowed in StudentProfile)
    from models import StudentProfile
    
    student1 = StudentProfile(
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
    )
    
    # Test 1: Overseas postgrad scholarship (should fail - undergrad student)
    action1 = EligibilityAction(
        student=student1,
        scholarship_name="JN Tata Endowment Loan Scholarship 2026-27",
        task="check_eligibility"
    )
    result1 = env.step(action1)
    obs1 = result1.observation
    
    # Should correctly identify course level mismatch
    course_level_check = any("Post Graduate" in str(c) or "postgraduate" in str(c).lower() 
                             for c in obs1.failed_criteria)
    
    # Test 2: Women tech scholarship (should pass - female, B.Tech, good marks)
    student2 = StudentProfile(
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
    student3 = StudentProfile(
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
    reasoning_score = 0.01  # Start with minimum valid score
    reasoning_score += 0.32 if course_level_check else 0.01
    reasoning_score += 0.32 if should_be_eligible else 0.01
    reasoning_score += 0.32 if marks_reasoning else 0.01
    
    return _ensure_valid_score(reasoning_score)


def grade_all_tasks() -> dict[str, float]:
    task1 = grade_task1()
    task2 = grade_task2()
    task3 = grade_task3()
    average = _ensure_valid_score((task1 + task2 + task3) / 3)
    return {"task1": task1, "task2": task2, "task3": task3, "average": average}
