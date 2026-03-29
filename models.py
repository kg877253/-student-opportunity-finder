from pydantic import BaseModel
from typing import List, Optional

# This is what the STUDENT provides
# Think of it like a form the student fills out
class StudentAction(BaseModel):
    name: str                    # Student's name
    gender: str                  # Male or Female
    category: str                # General, OBC, SC, ST, Minority
    state: str                   # Like Delhi, Maharashtra etc
    marks_class10: float         # Class 10 percentage
    marks_class12: float         # Class 12 percentage
    annual_income: float         # Family income per year
    course_level: str            # Undergraduate, Postgraduate etc
    course_name: str             # Like B.Tech, B.Sc etc
    age: int                     # Student's age
    task: str                    # Which task? "find_scholarships" or "find_exams"

# This is ONE scholarship result
class ScholarshipResult(BaseModel):
    name: str                    # Scholarship name
    amount: str                  # Amount in rupees
    deadline: str                # Last date to apply
    match_score: float           # How well does student match? 0.0 to 1.0
    match_reason: str            # Why does student match?

# This is what the AI RETURNS back to student
class ScholarshipObservation(BaseModel):
    matched_scholarships: List[ScholarshipResult]   # List of matching scholarships
    total_found: int                                 # How many found
    message: str                                     # A helpful message
    done: bool                                       # Is the task complete?
    reward: float                                    # Score 0.0 to 1.0

# This keeps track of the current game state
class EnvironmentState(BaseModel):
    episode_id: str              # Unique ID for this session
    step_count: int              # How many steps taken
    current_task: str            # Which task is running
    total_reward: float          # Total reward so far
# Add these at the bottom of models.py

# This is ONE exam result
class ExamResult(BaseModel):
    name: str                    # Exam name
    full_name: str               # Full name of exam
    deadline: str                # Last date to apply
    exam_type: str               # Government Job, Entrance etc
    salary_range: str            # Salary if it's a job exam
    match_score: float           # How well student matches 0.0 to 1.0
    match_reason: str            # Why student matches or not
    age_relaxation: str          # Any age relaxation for category

# This is what AI returns for exam finder
class ExamObservation(BaseModel):
    matched_exams: List[ExamResult]     # List of matching exams
    total_found: int                     # How many found
    message: str                         # Helpful message
    done: bool                           # Is task complete
    reward: float                        # Score 0.0 to 1.0

# This is for Task 3 - Eligibility Checker
class EligibilityAction(BaseModel):
    student: StudentAction               # Student profile
    scholarship_name: str                # Which scholarship to check

# This is what AI returns for eligibility check
class EligibilityObservation(BaseModel):
    scholarship_name: str                # Scholarship being checked
    is_eligible: bool                    # Eligible or not
    eligibility_score: float             # Score 0.0 to 1.0
    passed_criteria: List[str]           # What criteria student passed
    failed_criteria: List[str]           # What criteria student failed
    message: str                         # Final verdict message
    done: bool                           # Is task complete
    reward: float                        # Score 0.0 to 1.0