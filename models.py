from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field


Gender = Literal["Male", "Female", "Other"]
Category = Literal["General", "OBC", "SC", "ST", "Minority"]
SearchTaskName = Literal["find_scholarships", "find_exams"]
CourseLevel = Literal[
    "Class 10",
    "Class 12",
    "Undergraduate",
    "Graduation",
    "Postgraduate",
    "Post Graduate",
    "PG Diploma",
]
FocusArea = Literal["marks", "income", "age", "course"]


class StudentProfile(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=100)
    gender: Gender
    category: Category
    state: str = Field(min_length=2, max_length=100)
    marks_class10: float = Field(ge=0, le=100)
    marks_class12: float = Field(ge=0, le=100)
    annual_income: float = Field(ge=0)
    course_level: CourseLevel
    course_name: str = Field(min_length=2, max_length=100)
    age: int = Field(ge=0, le=100)

    current_marks: float | None = Field(default=None, ge=0, le=100)
    previous_marks: float | None = Field(default=None, ge=0, le=100)
    undergraduate_marks: float | None = Field(default=None, ge=0, le=100)
    year_of_study: int | None = Field(default=None, ge=1, le=10)
    attendance_percentage: float | None = Field(default=None, ge=0, le=100)
    study_location: str = Field(default="India", min_length=2, max_length=100)
    domicile_state: str | None = Field(default=None, min_length=2, max_length=100)
    college_type: str | None = Field(default=None, min_length=2, max_length=100)


class StudentAction(StudentProfile):
    task: SearchTaskName


class EligibilityAction(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    task: Literal["check_eligibility"] = "check_eligibility"
    student: StudentProfile
    scholarship_name: str = Field(min_length=2, max_length=200)


EnvironmentAction = Annotated[StudentAction | EligibilityAction, Field(discriminator="task")]


class ScholarshipResult(BaseModel):
    name: str
    amount: str
    deadline: str
    match_score: float = Field(ge=0, le=1)
    match_reason: str


class ScholarshipObservation(BaseModel):
    matched_scholarships: list[ScholarshipResult]
    total_found: int
    message: str
    done: bool
    reward: float = Field(ge=0, le=1)


class ExamResult(BaseModel):
    name: str
    full_name: str
    deadline: str
    exam_type: str
    salary_range: str
    match_score: float = Field(ge=0, le=1)
    match_reason: str
    age_relaxation: str


class ExamObservation(BaseModel):
    matched_exams: list[ExamResult]
    total_found: int
    message: str
    done: bool
    reward: float = Field(ge=0, le=1)


class EligibilityObservation(BaseModel):
    scholarship_name: str
    is_eligible: bool
    eligibility_score: float = Field(ge=0, le=1)
    passed_criteria: list[str]
    failed_criteria: list[str]
    manual_review_criteria: list[str] = Field(default_factory=list)
    message: str
    done: bool
    reward: float = Field(ge=0, le=1)


class EnvironmentState(BaseModel):
    episode_id: str
    step_count: int
    current_task: str
    total_reward: float


class StepInfo(BaseModel):
    episode_id: str
    current_task: str
    step_count: int
    total_reward: float
    notes: list[str] = Field(default_factory=list)


class StepResult(BaseModel):
    observation: ScholarshipObservation | ExamObservation | EligibilityObservation
    reward: float = Field(ge=0, le=1)
    done: bool
    info: StepInfo


class FeedbackAction(BaseModel):
    reward: float = Field(ge=0, le=1)
    focus_area: FocusArea | None = None
