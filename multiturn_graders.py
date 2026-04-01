from multiturn_environment import MultiTurnScholarshipGuidanceEnvironment


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
    return max(0.0, min(1.0, round(result.info.total_reward / 2.0, 2)))


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
    average = round((easy + medium + hard) / 3, 2)
    return {"easy": easy, "medium": medium, "hard": hard, "average": average}
