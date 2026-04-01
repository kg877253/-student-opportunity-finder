from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


MultiTurnTaskName = Literal[
    "easy_scholarship_shortlist",
    "medium_exam_guidance",
    "hard_mixed_guidance",
]
Difficulty = Literal["easy", "medium", "hard"]
GuidanceMode = Literal["scholarship", "exam", "mixed"]
ProfileField = Literal[
    "gender",
    "category",
    "state",
    "marks_class10",
    "marks_class12",
    "annual_income",
    "course_level",
    "course_name",
    "age",
    "current_marks",
    "year_of_study",
    "study_location",
    "college_type",
    "domicile_state",
]


class ResetRequest(BaseModel):
    task_name: MultiTurnTaskName = "easy_scholarship_shortlist"


class AskProfileFieldAction(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    action_type: Literal["ask_profile_field"] = "ask_profile_field"
    field_name: ProfileField


class DraftGuidanceAction(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    action_type: Literal["draft_guidance"] = "draft_guidance"
    scholarship_names: list[str] = Field(default_factory=list, max_length=5)
    exam_names: list[str] = Field(default_factory=list, max_length=5)


class FinalizeGuidanceAction(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    action_type: Literal["finalize_guidance"] = "finalize_guidance"
    scholarship_names: list[str] = Field(default_factory=list, max_length=5)
    exam_names: list[str] = Field(default_factory=list, max_length=5)
    primary_scholarship: str | None = Field(default=None, min_length=2, max_length=200)


MultiTurnAction = Annotated[
    AskProfileFieldAction | DraftGuidanceAction | FinalizeGuidanceAction,
    Field(discriminator="action_type"),
]


class GuidanceObservation(BaseModel):
    task_name: MultiTurnTaskName
    difficulty: Difficulty
    guidance_mode: GuidanceMode
    goal: str
    revealed_profile: dict[str, str | int | float | None]
    missing_fields: list[ProfileField]
    critical_missing_fields: list[ProfileField]
    remaining_steps: int
    last_action_summary: str
    draft_scholarships: list[str] = Field(default_factory=list)
    draft_exams: list[str] = Field(default_factory=list)
    guidance_messages: list[str] = Field(default_factory=list)
    available_actions: list[str] = Field(default_factory=list)
    done: bool
    reward: float = Field(ge=-1.0, le=1.0)


class GuidanceInfo(BaseModel):
    episode_id: str
    task_name: MultiTurnTaskName
    step_count: int
    max_steps: int
    total_reward: float = Field(ge=-10.0, le=10.0)
    notes: list[str] = Field(default_factory=list)


class GuidanceStepResult(BaseModel):
    observation: GuidanceObservation
    reward: float = Field(ge=-1.0, le=1.0)
    done: bool
    info: GuidanceInfo


class GuidanceEnvironmentState(BaseModel):
    episode_id: str
    task_name: MultiTurnTaskName
    difficulty: Difficulty
    guidance_mode: GuidanceMode
    step_count: int
    max_steps: int
    total_reward: float = Field(ge=-10.0, le=10.0)
    done: bool
    revealed_fields: list[ProfileField]
    missing_fields: list[ProfileField]
    critical_fields: list[ProfileField]
    draft_scholarships: list[str]
    draft_exams: list[str]
    full_student_profile: dict[str, str | int | float | None]
    target_scholarships: list[str]
    target_exams: list[str]
    primary_scholarship: str | None = None
    forbidden_scholarships: list[str] = Field(default_factory=list)
    forbidden_exams: list[str] = Field(default_factory=list)
