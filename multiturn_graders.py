from multiturn_environment import MultiTurnScholarshipGuidanceEnvironment


def _ensure_valid_score(score: float) -> float:
    """CRITICAL: Ensure score is strictly between 0 and 1 (exclusive)."""
    if score <= 0.0:
        return 0.01
    if score >= 1.0:
        return 0.99
    return round(score, 2)


def _play_reference_episode(task_name: str) -> float:
    env = MultiTurnScholarshipGuidanceEnvironment()
    env.reset(task_name)
    state = env.state_snapshot()

    for field_name in state.critical_fields:
        env.step({"action_type": "ask_profile_field", "field_name": field_name})

    state = env.state_snapshot()
    env.step(
        {
            "action_type": "draft_guidance",
            "scholarship_names": state.target_scholarships,
            "exam_names": state.target_exams,
        }
    )
    result = env.step(
        {
            "action_type": "finalize_guidance",
            "scholarship_names": state.target_scholarships,
            "exam_names": state.target_exams,
            "primary_scholarship": state.primary_scholarship,
        }
    )
    return _ensure_valid_score(result.info.total_reward / 2.0)


def grade_easy_task() -> float:
    return _play_reference_episode("easy_scholarship_shortlist")


def grade_medium_task() -> float:
    return _play_reference_episode("medium_exam_guidance")


def grade_hard_task() -> float:
    return _play_reference_episode("hard_mixed_guidance")


def grade_all_multiturn_tasks() -> dict[str, float]:
    easy = grade_easy_task()
    medium = grade_medium_task()
    hard = grade_hard_task()
    average = _ensure_valid_score((easy + medium + hard) / 3)
    return {"easy": easy, "medium": medium, "hard": hard, "average": average}
