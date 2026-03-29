from environment import ScholarshipEnvironment
from models import StudentAction, EligibilityAction


def grade_task1(student_profile: dict) -> float:
    env = ScholarshipEnvironment()
    env.reset()
    student = StudentAction(**student_profile)
    student.task = "find_scholarships"
    result = env.step(student)
    if result.total_found == 0:
        return 0.0
    elif result.total_found >= 3:
        return 1.0
    else:
        return result.total_found / 3


def grade_task2(student_profile: dict) -> float:
    env = ScholarshipEnvironment()
    env.reset()
    student = StudentAction(**student_profile)
    student.task = "find_exams"
    result = env.step(student)
    if result.total_found == 0:
        return 0.0
    elif result.total_found >= 4:
        return 1.0
    else:
        return result.total_found / 4


def grade_task3(student_profile: dict, scholarship_name: str) -> float:
    env = ScholarshipEnvironment()
    env.reset()
    student = StudentAction(**student_profile)
    action = EligibilityAction(
        student=student,
        scholarship_name=scholarship_name
    )
    result = env.step(action)
    return result.eligibility_score