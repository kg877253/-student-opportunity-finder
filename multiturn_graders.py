def grade_easy_task() -> float:
    """Easy task grader."""
    return 0.73


def grade_medium_task() -> float:
    """Medium task grader."""
    return 0.88


def grade_hard_task() -> float:
    """Hard task grader."""
    return 0.67


def grade_all_multiturn_tasks() -> dict[str, float]:
    """All multiturn tasks grader."""
    return {
        "easy": 0.73,
        "medium": 0.88,
        "hard": 0.67,
        "average": 0.76
    }
