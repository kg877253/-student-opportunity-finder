import uuid

from exams_data import exams
from models import (
    EligibilityAction,
    EligibilityObservation,
    EnvironmentState,
    ExamObservation,
    ExamResult,
    ScholarshipObservation,
    ScholarshipResult,
    StepInfo,
    StepResult,
    StudentAction,
)
from scholarships_data import scholarships


QUALIFICATION_LEVELS = {
    "Class 10": 1,
    "Class 12": 2,
    "Diploma": 2,
    "Undergraduate": 3,
    "Graduation": 3,
    "Class 12 or Diploma or Graduation": 3,
    "Postgraduate": 4,
    "Post Graduate": 4,
    "PG Diploma": 4,
}


class ScholarshipEnvironment:
    def __init__(self):
        self.state = None
        self.weights = {
            "marks": 1.0,
            "income": 1.0,
            "age": 1.0,
            "course": 1.0,
        }
        self.reset()

    def reset(self):
        self.state = EnvironmentState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            current_task="waiting",
            total_reward=0.0,
        )
        return self.state

    def state_snapshot(self):
        return self.state

    def update_weights(self, reward: float, focus_area: str | None = None):
        delta = 0.1 if reward >= 0.7 else -0.05
        targets = [focus_area] if focus_area in self.weights else list(self.weights.keys())

        for key in targets:
            self.weights[key] = max(0.1, self.weights[key] + delta)

        total = sum(self.weights.values())
        for key in self.weights:
            self.weights[key] = round(self.weights[key] / total, 4)

    def step(self, action: StudentAction | EligibilityAction) -> StepResult:
        if self.state is None:
            self.reset()

        self.state.step_count += 1

        if isinstance(action, EligibilityAction):
            self.state.current_task = action.task
            observation = self._check_eligibility(action)
            return self._to_step_result(observation)

        self.state.current_task = action.task
        if action.task == "find_scholarships":
            observation = self._find_scholarships(action)
            return self._to_step_result(observation)
        if action.task == "find_exams":
            observation = self._find_exams(action)
            return self._to_step_result(observation)

        observation = ScholarshipObservation(
            matched_scholarships=[],
            total_found=0,
            message="Unknown task. Use find_scholarships or find_exams.",
            done=True,
            reward=0.0,
        )
        return self._to_step_result(observation, notes=["Unknown task"])

    def _to_step_result(self, observation, notes: list[str] | None = None) -> StepResult:
        return StepResult(
            observation=observation,
            reward=observation.reward,
            done=observation.done,
            info=StepInfo(
                episode_id=self.state.episode_id,
                current_task=self.state.current_task,
                step_count=self.state.step_count,
                total_reward=round(self.state.total_reward, 2),
                notes=notes or [],
            ),
        )

    def _find_scholarships(self, action: StudentAction) -> ScholarshipObservation:
        matched = []

        for scholarship in scholarships:
            score, reason = self._calculate_scholarship_match(action, scholarship)
            if score > 0.3:
                matched.append(
                    ScholarshipResult(
                        name=scholarship["name"],
                        amount=str(scholarship.get("amount", "Check website")),
                        deadline=scholarship["deadline"],
                        match_score=round(score, 2),
                        match_reason=reason,
                    )
                )

        matched.sort(key=lambda item: item.match_score, reverse=True)

        top_scores = [item.match_score for item in matched[:3]]
        average_top_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
        coverage = min(1.0, len(matched) / 5)
        reward = round(min(1.0, 0.65 * average_top_score + 0.35 * coverage), 2)
        self.state.total_reward += reward

        return ScholarshipObservation(
            matched_scholarships=matched,
            total_found=len(matched),
            message=f"Found {len(matched)} scholarships for you.",
            done=True,
            reward=reward,
        )
                    )
                )

        matched.sort(key=lambda item: item.match_score, reverse=True)

        top_scores = [item.match_score for item in matched[:3]]
        average_top_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
        coverage = min(1.0, len(matched) / 5)
        reward = round(min(1.0, 0.65 * average_top_score + 0.35 * coverage), 2)
        self.state.total_reward += reward

        return ScholarshipObservation(
            matched_scholarships=matched,
            total_found=len(matched),
            message=f"Found {len(matched)} scholarships for you.",
            done=True,
            reward=reward,
        )

    def _calculate_scholarship_match(self, action: StudentAction, scholarship: dict):
        score = 1.0
        reasons = []
        issues = []
        manual_checks = []

        basic_failure = self._apply_basic_filters(
            action=action,
            item=scholarship,
            item_type="scholarship",
            issues=issues,
            reasons=reasons,
        )
        if basic_failure:
            return 0.0, issues[0]

        score = self._apply_mark_threshold(
            value=action.marks_class10,
            minimum=scholarship.get("min_marks_class10"),
            score=score,
            penalty=0.15 * self.weights["marks"],
            success_message=f"Class 10 marks {action.marks_class10}% meet the requirement",
            failure_message=f"Need {scholarship.get('min_marks_class10')}% in Class 10 but you have {action.marks_class10}%",
            reasons=reasons,
            issues=issues,
        )
        score = self._apply_mark_threshold(
            value=action.marks_class12,
            minimum=scholarship.get("min_marks_class12"),
            score=score,
            penalty=0.2 * self.weights["marks"],
            success_message=f"Class 12 marks {action.marks_class12}% meet the requirement",
            failure_message=f"Need {scholarship.get('min_marks_class12')}% in Class 12 but you have {action.marks_class12}%",
            reasons=reasons,
            issues=issues,
        )

        score = self._apply_optional_mark_threshold(
            label="current year marks",
            value=action.current_marks,
            minimum=scholarship.get("min_marks_current"),
            score=score,
            reasons=reasons,
            issues=issues,
            manual_checks=manual_checks,
        )
        score = self._apply_optional_mark_threshold(
            label="previous year marks",
            value=action.previous_marks,
            minimum=scholarship.get("min_marks_previous"),
            score=score,
            reasons=reasons,
            issues=issues,
            manual_checks=manual_checks,
        )
        score = self._apply_optional_mark_threshold(
            label="undergraduate marks",
            value=action.undergraduate_marks,
            minimum=scholarship.get("min_marks_undergraduate"),
            score=score,
            reasons=reasons,
            issues=issues,
            manual_checks=manual_checks,
        )

        max_income = scholarship.get("max_income")
        if max_income is not None:
            if action.annual_income > max_income:
                score -= 0.2 * self.weights["income"]
                issues.append(f"Income limit is {max_income} but yours is {action.annual_income}")
            else:
                reasons.append(f"Income {action.annual_income} is within the limit")

        min_age = scholarship.get("min_age", 0)
        max_age = scholarship.get("max_age", 99)
        if action.age < min_age or action.age > max_age:
            score -= 0.15 * self.weights["age"]
            issues.append(f"Age requirement is {min_age} to {max_age} but you are {action.age}")
        else:
            reasons.append(f"Age {action.age} is within the limit")

        score = self._apply_manual_rule(
            student_value=action.year_of_study,
            expected_value=scholarship.get("year"),
            label="year of study",
            score=score,
            reasons=reasons,
            issues=issues,
            manual_checks=manual_checks,
        )
        score = self._apply_manual_rule(
            student_value=action.study_location,
            expected_value=scholarship.get("study_location"),
            label="study location",
            score=score,
            reasons=reasons,
            issues=issues,
            manual_checks=manual_checks,
        )
        score = self._apply_manual_rule(
            student_value=action.college_type,
            expected_value=scholarship.get("college_type"),
            label="college type",
            score=score,
            reasons=reasons,
            issues=issues,
            manual_checks=manual_checks,
            partial_match=True,
        )
        score = self._apply_manual_rule(
            student_value=action.domicile_state or action.state,
            expected_value=scholarship.get("domicile_required"),
            label="domicile",
            score=score,
            reasons=reasons,
            issues=issues,
            manual_checks=manual_checks,
        )

        if scholarship.get("min_attendance") is not None:
            if action.attendance_percentage is None:
                score -= 0.05
                manual_checks.append(
                    f"Attendance of at least {scholarship['min_attendance']}% is required for full verification"
                )
            elif action.attendance_percentage < scholarship["min_attendance"]:
                score -= 0.1
                issues.append(
                    f"Attendance must be at least {scholarship['min_attendance']}% but you have {action.attendance_percentage}%"
                )
            else:
                reasons.append(f"Attendance {action.attendance_percentage}% meets the requirement")

        score = max(0.0, min(1.0, score))
        if issues:
            reason = "Issues: " + ", ".join(issues)
        else:
            reason = "Great match! " + ", ".join(reasons)
        if manual_checks:
            reason += ". Additional verification: " + ", ".join(manual_checks)
        return score, reason

    def _find_exams(self, action: StudentAction) -> ExamObservation:
        matched = []

        for exam in exams:
            score, reason, age_relaxation = self._calc_exam_match(action, exam)
            if score > 0.3:
                matched.append(
                    ExamResult(
                        name=exam["name"],
                        full_name=exam["full_name"],
                        deadline=exam["deadline"],
                        exam_type=exam["exam_type"],
                        salary_range=exam["salary_range"],
                        match_score=round(score, 2),
                        match_reason=reason,
                        age_relaxation=age_relaxation,
                    )
                )

        matched.sort(key=lambda item: item.match_score, reverse=True)
        top_scores = [item.match_score for item in matched[:3]]
        average_top_score = sum(top_scores) / len(top_scores) if top_scores else 0.0
        coverage = min(1.0, len(matched) / 5)
        reward = round(min(1.0, 0.55 * average_top_score + 0.45 * coverage), 2)
        self.state.total_reward += reward

        return ExamObservation(
            matched_exams=matched,
            total_found=len(matched),
            message=f"Found {len(matched)} exams you can apply for.",
            done=True,
            reward=reward,
        )

    def _calculate_exam_match(self, action: StudentAction, exam: dict):
        score = 1.0
        reasons = []
        issues = []
        age_relaxation = "No relaxation"

        basic_failure = self._apply_basic_filters(
            action=action,
            item=exam,
            item_type="exam",
            issues=issues,
            reasons=reasons,
        )
        if basic_failure:
            return 0.0, issues[0], age_relaxation

        relaxation = exam.get("category_age_relaxation", {})
        extra_years = relaxation.get(action.category, 0)
        effective_max_age = exam.get("max_age", 99) + extra_years
        if extra_years > 0:
            age_relaxation = f"{extra_years} years relaxation for {action.category} category"

        if action.age < exam.get("min_age", 0):
            score -= 0.25
            issues.append(f"Minimum age is {exam.get('min_age')} but you are {action.age}")
        elif action.age > effective_max_age:
            score -= 0.25
            issues.append(f"Maximum age is {effective_max_age} but you are {action.age}")
        else:
            reasons.append(f"Age {action.age} is within the limit")

        min_qualification = exam.get("min_qualification", "Class 12")
        student_qualification = QUALIFICATION_LEVELS.get(action.course_level, 2)
        required_qualification = QUALIFICATION_LEVELS.get(min_qualification, 2)

        if student_qualification < required_qualification:
            score -= 0.35
            issues.append(f"Need {min_qualification} but you have {action.course_level}")
        else:
            reasons.append(f"Qualification {action.course_level} meets the requirement")

        score = max(0.0, min(1.0, score))
        if issues:
            reason = "Issues: " + ", ".join(issues)
        else:
            reason = "Great match! " + ", ".join(reasons)
        return score, reason, age_relaxation

    def _check_eligibility(self, action: EligibilityAction) -> EligibilityObservation:
        student = action.student
        scholarship = next(
            (item for item in scholarships if self._normalize(item["name"]) == self._normalize(action.scholarship_name)),
            None,
        )

        if not scholarship:
            return EligibilityObservation(
                scholarship_name=action.scholarship_name,
                is_eligible=False,
                eligibility_score=0.0,
                passed_criteria=[],
                failed_criteria=["Scholarship not found in database"],
                manual_review_criteria=[],
                message="Scholarship not found. Please check the name and try again.",
                done=True,
                reward=0.0,
            )

        passed = []
        failed = []
        manual = []

        self._append_basic_eligibility_checks(student, scholarship, passed, failed)
        self._append_numeric_eligibility_check("Class 10 marks", student.marks_class10, scholarship.get("min_marks_class10"), passed, failed)
        self._append_numeric_eligibility_check("Class 12 marks", student.marks_class12, scholarship.get("min_marks_class12"), passed, failed)
        self._append_max_value_check("Income", student.annual_income, scholarship.get("max_income"), passed, failed)
        self._append_range_check("Age", student.age, scholarship.get("min_age", 0), scholarship.get("max_age", 99), passed, failed)

        self._append_optional_numeric_check("Current marks", student.current_marks, scholarship.get("min_marks_current"), passed, failed, manual)
        self._append_optional_numeric_check("Previous marks", student.previous_marks, scholarship.get("min_marks_previous"), passed, failed, manual)
        self._append_optional_numeric_check("Undergraduate marks", student.undergraduate_marks, scholarship.get("min_marks_undergraduate"), passed, failed, manual)
        self._append_optional_membership_check("Year of study", student.year_of_study, scholarship.get("year"), passed, failed, manual)
        self._append_optional_exact_check("Study location", student.study_location, scholarship.get("study_location"), passed, failed, manual)
        self._append_optional_exact_check("Domicile", student.domicile_state or student.state, scholarship.get("domicile_required"), passed, failed, manual)
        self._append_optional_exact_check(
            "College type",
            student.college_type,
            scholarship.get("college_type"),
            passed,
            failed,
            manual,
            partial_match=True,
        )

        if scholarship.get("min_attendance") is not None:
            if student.attendance_percentage is None:
                manual.append(
                    f"Attendance must be at least {scholarship['min_attendance']}%, but it was not provided"
                )
            elif student.attendance_percentage >= scholarship["min_attendance"]:
                passed.append(
                    f"Attendance: {student.attendance_percentage}% meets minimum {scholarship['min_attendance']}%"
                )
            else:
                failed.append(
                    f"Attendance: need {scholarship['min_attendance']}% but you have {student.attendance_percentage}%"
                )

        total_criteria = len(passed) + len(failed) + len(manual)
        passed_ratio = len(passed) / total_criteria if total_criteria else 0.0
        manual_penalty = 0.05 * len(manual)
        reward = round(max(0.0, min(1.0, passed_ratio - manual_penalty)), 2)
        is_eligible = not failed and not manual
        self.state.total_reward += reward

        if is_eligible:
            message = f"Congratulations! You are eligible for {action.scholarship_name}. Apply before {scholarship['deadline']}."
        elif failed:
            message = f"You are not yet eligible for {action.scholarship_name}. Fix the failed criteria and try again."
        else:
            message = f"{action.scholarship_name} needs a few more details before eligibility can be confirmed."

        return EligibilityObservation(
            scholarship_name=action.scholarship_name,
            is_eligible=is_eligible,
            eligibility_score=reward,
            passed_criteria=passed,
            failed_criteria=failed,
            manual_review_criteria=manual,
            message=message,
            done=True,
            reward=reward,
        )

    def _apply_basic_filters(self, action: StudentAction, item: dict, item_type: str, issues: list[str], reasons: list[str]):
        label = item_type.capitalize()

        gender = item.get("gender", "All")
        if not self._matches_value(action.gender, gender):
            issues.append(f"This {item_type} is only for {gender} candidates")
            return True
        reasons.append(f"{label} gender criteria match")

        state = item.get("state", "All India")
        if not self._matches_value(action.state, state):
            issues.append(f"This {item_type} is only for {state} candidates")
            return True
        reasons.append(f"{label} state criteria match")

        category = item.get("category", "All")
        if not self._matches_value(action.category, category):
            issues.append(f"This {item_type} is for {category} category only")
            return True
        reasons.append(f"{label} category criteria match")

        course_level = item.get("course_level")
        if course_level and not self._matches_value(action.course_level, course_level):
            issues.append(f"This {item_type} is for {course_level} only")
            return True
        if course_level:
            reasons.append("Course level matches")

        allowed_courses = item.get("allowed_courses")
        if allowed_courses and not self._matches_course_name(action.course_name, allowed_courses):
            issues.append(f"This {item_type} is for {allowed_courses} courses only")
            return True
        if allowed_courses:
            reasons.append("Course name matches")
        return False

    def _append_basic_eligibility_checks(self, student: StudentAction, scholarship: dict, passed: list[str], failed: list[str]):
        self._append_exact_check("Gender", student.gender, scholarship.get("gender", "All"), passed, failed)
        self._append_exact_check("State", student.state, scholarship.get("state", "All India"), passed, failed)
        self._append_exact_check("Category", student.category, scholarship.get("category", "All"), passed, failed)
        if scholarship.get("course_level"):
            self._append_exact_check("Course level", student.course_level, scholarship.get("course_level"), passed, failed)
        if scholarship.get("allowed_courses"):
            self._append_course_check(student.course_name, scholarship.get("allowed_courses"), passed, failed)

    def _append_exact_check(self, label: str, value, expected, passed: list[str], failed: list[str]):
        if expected is None:
            return
        if self._matches_value(value, expected):
            passed.append(f"{label}: {value} is accepted")
        else:
            failed.append(f"{label}: needs {expected} but you have {value}")

    def _append_course_check(self, value: str, expected, passed: list[str], failed: list[str]):
        if self._matches_course_name(value, expected):
            passed.append(f"Course: {value} is accepted")
        else:
            failed.append(f"Course: needs one of {expected} but you have {value}")

    def _append_numeric_eligibility_check(self, label: str, value: float, minimum, passed: list[str], failed: list[str]):
        if minimum is None:
            return
        if value >= minimum:
            passed.append(f"{label}: your {value}% meets minimum {minimum}%")
        else:
            failed.append(f"{label}: need {minimum}% but you have {value}%")

    def _append_optional_numeric_check(self, label: str, value: float | None, minimum, passed: list[str], failed: list[str], manual: list[str]):
        if minimum is None:
            return
        if value is None:
            manual.append(f"{label}: minimum {minimum}% is required, but this detail was not provided")
            return
        if value >= minimum:
            passed.append(f"{label}: your {value}% meets minimum {minimum}%")
        else:
            failed.append(f"{label}: need {minimum}% but you have {value}%")

    def _append_max_value_check(self, label: str, value: float, maximum, passed: list[str], failed: list[str]):
        if maximum is None:
            return
        if value <= maximum:
            passed.append(f"{label}: {value} is within limit {maximum}")
        else:
            failed.append(f"{label}: limit is {maximum} but yours is {value}")

    def _append_range_check(self, label: str, value: float, minimum: float, maximum: float, passed: list[str], failed: list[str]):
        if minimum <= value <= maximum:
            passed.append(f"{label}: {value} is within limit {minimum} to {maximum}")
        else:
            failed.append(f"{label}: limit is {minimum} to {maximum} but you are {value}")

    def _append_optional_membership_check(self, label: str, value, expected, passed: list[str], failed: list[str], manual: list[str]):
        if expected is None:
            return
        if value is None:
            manual.append(f"{label}: must be one of {expected}, but this detail was not provided")
            return
        if self._matches_value(value, expected):
            passed.append(f"{label}: {value} is accepted")
        else:
            failed.append(f"{label}: needs one of {expected} but you have {value}")

    def _append_optional_exact_check(
        self,
        label: str,
        value,
        expected,
        passed: list[str],
        failed: list[str],
        manual: list[str],
        partial_match: bool = False,
    ):
        if expected is None:
            return
        if value is None:
            manual.append(f"{label}: needs {expected}, but this detail was not provided")
            return
        if self._matches_value(value, expected, partial_match=partial_match):
            passed.append(f"{label}: {value} is accepted")
        else:
            failed.append(f"{label}: needs {expected} but you have {value}")

    def _apply_mark_threshold(
        self,
        value: float,
        minimum,
        score: float,
        penalty: float,
        success_message: str,
        failure_message: str,
        reasons: list[str],
        issues: list[str],
    ):
        if minimum is None:
            return score
        if value >= minimum:
            reasons.append(success_message)
            return score
        issues.append(failure_message)
        return score - penalty

    def _apply_optional_mark_threshold(
        self,
        label: str,
        value: float | None,
        minimum,
        score: float,
        reasons: list[str],
        issues: list[str],
        manual_checks: list[str],
    ):
        if minimum is None:
            return score
        if value is None:
            manual_checks.append(f"{label.title()} of at least {minimum}% is needed for full verification")
            return score - 0.05
        if value >= minimum:
            reasons.append(f"{label.title()} {value}% meets the requirement")
            return score
        issues.append(f"Need {minimum}% in {label} but you have {value}%")
        return score - 0.15

    def _apply_manual_rule(
        self,
        student_value,
        expected_value,
        label: str,
        score: float,
        reasons: list[str],
        issues: list[str],
        manual_checks: list[str],
        partial_match: bool = False,
    ):
        if expected_value is None:
            return score
        if student_value is None:
            manual_checks.append(f"{label.title()} needs {expected_value} for full verification")
            return score - 0.05
        if self._matches_value(student_value, expected_value, partial_match=partial_match):
            reasons.append(f"{label.title()} matches")
            return score
        issues.append(f"{label.title()} must be {expected_value} but you have {student_value}")
        return score - 0.15

    def _matches_course_name(self, course_name: str, allowed_courses):
        return self._matches_value(course_name, allowed_courses, partial_match=True)

    def _matches_value(self, actual, expected, partial_match: bool = False):
        if expected is None:
            return True

        actual_normalized = self._normalize(actual)
        expected_values = expected if isinstance(expected, list) else [expected]
        normalized_expected = [self._normalize(value) for value in expected_values]

        if any(value in {"all", "all india"} for value in normalized_expected):
            return True
        if partial_match:
            return any(
                actual_normalized == value or actual_normalized in value or value in actual_normalized
                for value in normalized_expected
            )
        return actual_normalized in normalized_expected

    def _normalize(self, value):
        return str(value).strip().lower()
