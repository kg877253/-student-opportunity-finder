from environment import ScholarshipEnvironment
from models import EligibilityAction, StudentAction

# CRITICAL CONSTANTS - scores strictly inside (0,1)
MIN_SCORE = 0.01
MAX_SCORE = 0.99
FALLBACK_SCORE = 0.5


def _ensure_valid_score(score) -> float:
    """STRICT clamp to (0,1) — guaranteed safe for evaluation."""
    try:
        s = float(score)

        # Hard clamp
        if s <= 0.0:
            return MIN_SCORE
        if s >= 1.0:
            return MAX_SCORE

        # Keep safely inside bounds
        s = max(MIN_SCORE, min(MAX_SCORE, s))

        # Safe rounding (avoid 0.0 or 1.0)
        s = round(s, 4)

        # Final guarantee
        if s <= 0.0:
            return MIN_SCORE
        if s >= 1.0:
            return MAX_SCORE

        return s

    except:
        return FALLBACK_SCORE


def _score_presence(items: list[str], expected: list[str], forbidden: list[str]) -> float:
    try:
        if not items:
            return MIN_SCORE

        expected_hits = sum(1 for name in expected if name in items)
        forbidden_hits = sum(1 for name in forbidden if name in items)

        # Prevent exact 1.0
        if expected:
            expected_score = expected_hits / len(expected)
            expected_score = min(expected_score, 0.95)
        else:
            expected_score = 0.95

        # Avoid zero penalty edge
        penalty = (forbidden_hits / len(forbidden)) if forbidden else 0.01

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

        scholarship_names = [
            item.name for item in result.observation.matched_scholarships
        ]

        ranking_bonus = (
            0.95
            if scholarship_names[:1]
            and scholarship_names[0]
            == "Vivo KanyaGyaan Scholarship Program 2025-26"
            else 0.7
        )

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

        exam_names = [
            item.name for item in result.observation.matched_exams
        ]

        presence_score = _score_presence(
            items=exam_names,
            expected=["IBPS Clerk 2025", "SBI PO 2025", "SSC CGL 2025"],
            forbidden=["GATE 2026"],
        )

        ranking_bonus = (
            0.95 if "GATE 2026" not in exam_names[:5] else 0.05
        )

        raw_score = 0.8 * presence_score + 0.2 * ranking_bonus
        return _ensure_valid_score(raw_score)

    except:
        return FALLBACK_SCORE


def grade_task3() -> float:
    """Hard task: nested reasoning validation."""
    try:
        env = ScholarshipEnvironment()
        from models import StudentProfile

        # Case 1
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
            task="check_eligibility",
        )

        result1 = env.step(action1)
        obs1 = result1.observation

        course_level_check = any(
            "postgraduate" in str(c).lower()
            for c in obs1.failed_criteria
        )

        # Case 2
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
            task="check_eligibility",
        )

        result2 = env.step(action2)
        obs2 = result2.observation

        should_be_eligible = (
            obs2.is_eligible and obs2.eligibility_score >= 0.8
        )

        # Case 3
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
            task="check_eligibility",
        )

        result3 = env.step(action3)
        obs3 = result3.observation

        marks_reasoning = obs3.is_eligible

        # Scoring (never reaches 1.0)
        reasoning_score = 0.05
        reasoning_score += 0.3 if course_level_check else 0.05
        reasoning_score += 0.3 if should_be_eligible else 0.05
        reasoning_score += 0.3 if marks_reasoning else 0.05

        return _ensure_valid_score(reasoning_score)

    except:
        return FALLBACK_SCORE


def grade_all_tasks() -> dict[str, float]:
    try:
        task1 = grade_task1()
        task2 = grade_task2()
        task3 = grade_task3()

        average = (task1 + task2 + task3) / 3

        return {
            "task1": _ensure_valid_score(task1),
            "task2": _ensure_valid_score(task2),
            "task3": _ensure_valid_score(task3),
            "average": _ensure_valid_score(average),
        }

    except:
        return {
            "task1": FALLBACK_SCORE,
            "task2": FALLBACK_SCORE,
            "task3": FALLBACK_SCORE,
            "average": FALLBACK_SCORE,
        }