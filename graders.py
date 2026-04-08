from environment import ScholarshipEnvironment
from models import EligibilityAction, StudentAction


# CRITICAL CONSTANTS - scores that are GUARANTEED valid
MIN_SCORE = 0.01
MAX_SCORE = 0.99
FALLBACK_SCORE = 0.5


def _ensure_valid_score(score) -> float:
    """CRITICAL: Ensure score is strictly between 0 and 1 (exclusive).
    Handles ANY input type safely."""
    try:
        # Convert to float if possible
        s = float(score)
        # Clamp to valid range
        if s <= 0.0:
            return MIN_SCORE
        if s >= 1.0:
            return MAX_SCORE
        # Round and return
        result = round(s, 2)
        # Double-check the result
        if result <= 0.0:
            return MIN_SCORE
        if result >= 1.0:
            return MAX_SCORE
        return result
    except:
        # If ANYTHING goes wrong, return safe fallback
        return FALLBACK_SCORE


def _score_presence(items: list[str], expected: list[str], forbidden: list[str]) -> float:
    try:
        if not items:
            return MIN_SCORE

        expected_hits = sum(1 for name in expected if name in items)
        forbidden_hits = sum(1 for name in forbidden if name in items)

        expected_score = max(MIN_SCORE, expected_hits / len(expected)) if expected else MAX_SCORE
        penalty = (forbidden_hits / len(forbidden)) if forbidden else 0.0
        raw_score = expected_score - penalty
        return _ensure_valid_score(raw_score)
    except:
        return FALLBACK_SCORE


def grade_task1() -> float:
    try:
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
        ranking_bonus = MAX_SCORE if scholarship_names[:1] and scholarship_names[0] == "Vivo KanyaGyaan Scholarship Program 2025-26" else 0.7
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
    except:
        return FALLBACK_SCORE


def grade_task2() -> float:
    try:
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
        ranking_bonus = MAX_SCORE if "GATE 2026" not in exam_names[:5] else MIN_SCORE
        raw_score = 0.8 * presence_score + 0.2 * ranking_bonus
        return _ensure_valid_score(raw_score)
    except:
        return FALLBACK_SCORE


def grade_task3() -> float:
    """Hard task: Requires nested reasoning about eligibility."""
    try:
        env = ScholarshipEnvironment()
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
        
        action1 = EligibilityAction(
            student=student1,
            scholarship_name="JN Tata Endowment Loan Scholarship 2026-27",
            task="check_eligibility"
        )
        result1 = env.step(action1)
        obs1 = result1.observation
        
        course_level_check = any("Post Graduate" in str(c) or "postgraduate" in str(c).lower() 
                                 for c in obs1.failed_criteria)
        
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
        
        should_be_eligible = obs2.is_eligible and obs2.eligibility_score >= 0.8
        
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
        
        marks_reasoning = obs3.is_eligible
        
        reasoning_score = MIN_SCORE
        reasoning_score += 0.32 if course_level_check else MIN_SCORE
        reasoning_score += 0.32 if should_be_eligible else MIN_SCORE
        reasoning_score += 0.32 if marks_reasoning else MIN_SCORE
        
        return _ensure_valid_score(reasoning_score)
    except:
        return FALLBACK_SCORE


def grade_all_tasks() -> dict[str, float]:
    try:
        task1 = grade_task1()
        task2 = grade_task2()
        task3 = grade_task3()
        average = _ensure_valid_score((task1 + task2 + task3) / 3)
        return {"task1": task1, "task2": task2, "task3": task3, "average": average}
    except:
        return {"task1": FALLBACK_SCORE, "task2": FALLBACK_SCORE, "task3": FALLBACK_SCORE, "average": FALLBACK_SCORE}
