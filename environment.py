import uuid
from models import (
    StudentAction,
    ScholarshipObservation,
    ScholarshipResult,
    ExamObservation,
    ExamResult,
    EligibilityAction,
    EligibilityObservation,
    EnvironmentState
)
from scholarships_data import scholarships
from exams_data import exams


class ScholarshipEnvironment:

    def __init__(self):
        self.state = None
        self.current_action = None
        # Auto reset on creation!
        self.reset()

    def reset(self):
        self.state = EnvironmentState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            current_task="waiting",
            total_reward=0.0
        )
        return self.state

    def step(self, action):
        # Safety check - reset if state is None
        if self.state is None:
            self.reset()

        self.state.step_count += 1

        if isinstance(action, EligibilityAction):
            self.state.current_task = "check_eligibility"
            return self._check_eligibility(action)

        elif isinstance(action, StudentAction):
            self.state.current_task = action.task

            if action.task == "find_scholarships":
                return self._find_scholarships(action)

            elif action.task == "find_exams":
                return self._find_exams(action)

            else:
                return self._unknown_task()

    def _find_scholarships(self, action: StudentAction):
        matched = []

        for scholarship in scholarships:
            score, reason = self._calculate_scholarship_match(action, scholarship)

            if score > 0.3:
                amount = str(scholarship.get("amount", "Check website"))
                matched.append(ScholarshipResult(
                    name=scholarship["name"],
                    amount=amount,
                    deadline=scholarship["deadline"],
                    match_score=round(score, 2),
                    match_reason=reason
                ))

        matched.sort(key=lambda x: x.match_score, reverse=True)
        reward = min(1.0, len(matched) / 5)
        self.state.total_reward += reward

        return ScholarshipObservation(
            matched_scholarships=matched,
            total_found=len(matched),
            message=f"Found {len(matched)} scholarships for you!",
            done=True,
            reward=reward
        )

    def _calculate_scholarship_match(self, action: StudentAction, scholarship: dict):
        score = 1.0
        reasons = []
        deductions = []

        if scholarship.get("gender") == "Female" and action.gender != "Female":
            return 0.0, "This scholarship is only for female students"

        schol_state = scholarship.get("state", "All India")
        if schol_state != "All India" and schol_state != action.state:
            return 0.0, f"This scholarship is only for {schol_state} students"

        schol_category = scholarship.get("category", "All")
        if schol_category != "All":
            if isinstance(schol_category, list):
                if action.category not in schol_category:
                    return 0.0, f"This scholarship is for {schol_category} category only"
            elif schol_category != action.category:
                return 0.0, f"This scholarship is for {schol_category} category only"

        min_marks = scholarship.get("min_marks_class12", 0)
        if action.marks_class12 < min_marks:
            score -= 0.4
            deductions.append(f"Need {min_marks}% in Class 12 but you have {action.marks_class12}%")
        else:
            reasons.append(f"Your Class 12 marks {action.marks_class12}% meet the requirement")

        max_income = scholarship.get("max_income", 99999999)
        if action.annual_income > max_income:
            score -= 0.4
            deductions.append(f"Income limit is {max_income} but yours is {action.annual_income}")
        else:
            reasons.append(f"Your income {action.annual_income} is within the limit")

        min_age = scholarship.get("min_age", 0)
        max_age = scholarship.get("max_age", 99)
        if action.age < min_age or action.age > max_age:
            score -= 0.3
            deductions.append(f"Age requirement is {min_age} to {max_age} but you are {action.age}")
        else:
            reasons.append(f"Your age {action.age} is within the limit")

        schol_courses = scholarship.get("course_level", ["All"])
        if "All" not in schol_courses and action.course_level not in schol_courses:
            score -= 0.3
            deductions.append(f"This scholarship is for {schol_courses} only")
        else:
            reasons.append(f"Your course level matches!")

        score = max(0.0, score)

        if deductions:
            reason = "Issues: " + ", ".join(deductions)
        else:
            reason = "Great match! " + ", ".join(reasons)

        return score, reason

    def _find_exams(self, action: StudentAction):
        matched = []

        for exam in exams:
            score, reason, age_relaxation = self._calculate_exam_match(action, exam)

            if score > 0.3:
                matched.append(ExamResult(
                    name=exam["name"],
                    full_name=exam["full_name"],
                    deadline=exam["deadline"],
                    exam_type=exam["exam_type"],
                    salary_range=exam["salary_range"],
                    match_score=round(score, 2),
                    match_reason=reason,
                    age_relaxation=age_relaxation
                ))

        matched.sort(key=lambda x: x.match_score, reverse=True)
        reward = min(1.0, len(matched) / 5)
        self.state.total_reward += reward

        return ExamObservation(
            matched_exams=matched,
            total_found=len(matched),
            message=f"Found {len(matched)} exams you can apply for!",
            done=True,
            reward=reward
        )

    def _calculate_exam_match(self, action: StudentAction, exam: dict):
        score = 1.0
        reasons = []
        deductions = []
        age_relaxation = "No relaxation"

        if exam.get("gender") == "Male" and action.gender != "Male":
            return 0.0, "This exam is only for male candidates", age_relaxation

        if exam.get("gender") == "Female" and action.gender != "Female":
            return 0.0, "This exam is only for female candidates", age_relaxation

        exam_state = exam.get("state", "All India")
        if exam_state != "All India" and exam_state != action.state:
            return 0.0, f"This exam is only for {exam_state} candidates", age_relaxation

        relaxation = exam.get("category_age_relaxation", {})
        extra_years = relaxation.get(action.category, 0)
        effective_max_age = exam["max_age"] + extra_years

        if extra_years > 0:
            age_relaxation = f"{extra_years} years relaxation for {action.category} category"

        if action.age < exam["min_age"]:
            score -= 0.4
            deductions.append(f"Minimum age is {exam['min_age']} but you are {action.age}")
        elif action.age > effective_max_age:
            score -= 0.4
            deductions.append(f"Maximum age is {effective_max_age} but you are {action.age}")
        else:
            reasons.append(f"Your age {action.age} is within the limit")

        min_qual = exam.get("min_qualification", "Class 12")
        qual_map = {
            "Class 10": 1,
            "Class 12": 2,
            "Undergraduate": 3,
            "Graduation": 3,
            "Postgraduate": 4,
            "Post Graduate": 4
        }
        student_qual_level = qual_map.get(action.course_level, 2)
        required_qual_level = qual_map.get(min_qual, 2)

        if student_qual_level < required_qual_level:
            score -= 0.5
            deductions.append(f"Need {min_qual} but you have {action.course_level}")
        else:
            reasons.append(f"Your qualification {action.course_level} meets the requirement")

        score = max(0.0, score)

        if deductions:
            reason = "Issues: " + ", ".join(deductions)
        else:
            reason = "Great match! " + ", ".join(reasons)

        return score, reason, age_relaxation

    def _check_eligibility(self, action: EligibilityAction):
        student = action.student
        target_scholarship = None

        for scholarship in scholarships:
            if scholarship["name"].lower() == action.scholarship_name.lower():
                target_scholarship = scholarship
                break

        if not target_scholarship:
            return EligibilityObservation(
                scholarship_name=action.scholarship_name,
                is_eligible=False,
                eligibility_score=0.0,
                passed_criteria=[],
                failed_criteria=["Scholarship not found in database"],
                message="Scholarship not found! Please check the name.",
                done=True,
                reward=0.0
            )

        passed = []
        failed = []
        total_criteria = 0
        passed_count = 0

        total_criteria += 1
        schol_gender = target_scholarship.get("gender", "All")
        if schol_gender == "All" or schol_gender == student.gender:
            passed.append(f"Gender: {student.gender} is accepted")
            passed_count += 1
        else:
            failed.append(f"Gender: Scholarship needs {schol_gender} but you are {student.gender}")

        total_criteria += 1
        schol_state = target_scholarship.get("state", "All India")
        if schol_state == "All India" or schol_state == student.state:
            passed.append(f"State: {student.state} is accepted")
            passed_count += 1
        else:
            failed.append(f"State: Scholarship needs {schol_state} but you are from {student.state}")

        total_criteria += 1
        schol_category = target_scholarship.get("category", "All")
        if schol_category == "All":
            passed.append(f"Category: All categories accepted")
            passed_count += 1
        elif isinstance(schol_category, list):
            if student.category in schol_category:
                passed.append(f"Category: {student.category} is accepted")
                passed_count += 1
            else:
                failed.append(f"Category: Needs {schol_category} but you are {student.category}")
        else:
            if schol_category == student.category:
                passed.append(f"Category: {student.category} is accepted")
                passed_count += 1
            else:
                failed.append(f"Category: Needs {schol_category} but you are {student.category}")

        total_criteria += 1
        min_marks = target_scholarship.get("min_marks_class12", 0)
        if student.marks_class12 >= min_marks:
            passed.append(f"Marks: Your {student.marks_class12}% meets minimum {min_marks}%")
            passed_count += 1
        else:
            failed.append(f"Marks: Need {min_marks}% but you have {student.marks_class12}%")

        total_criteria += 1
        max_income = target_scholarship.get("max_income", 99999999)
        if student.annual_income <= max_income:
            passed.append(f"Income: Your income {student.annual_income} is within limit {max_income}")
            passed_count += 1
        else:
            failed.append(f"Income: Limit is {max_income} but yours is {student.annual_income}")

        total_criteria += 1
        min_age = target_scholarship.get("min_age", 0)
        max_age = target_scholarship.get("max_age", 99)
        if min_age <= student.age <= max_age:
            passed.append(f"Age: Your age {student.age} is within limit {min_age} to {max_age}")
            passed_count += 1
        else:
            failed.append(f"Age: Limit is {min_age} to {max_age} but you are {student.age}")

        eligibility_score = round(passed_count / total_criteria, 2)
        is_eligible = eligibility_score >= 0.8

        if is_eligible:
            message = f"Congratulations! You are eligible for {action.scholarship_name}! Apply before {target_scholarship['deadline']}!"
        elif eligibility_score >= 0.5:
            message = f"You are partially eligible for {action.scholarship_name}. Fix the failed criteria to apply!"
        else:
            message = f"Sorry! You are not eligible for {action.scholarship_name} right now."

        reward = eligibility_score
        self.state.total_reward += reward

        return EligibilityObservation(
            scholarship_name=action.scholarship_name,
            is_eligible=is_eligible,
            eligibility_score=eligibility_score,
            passed_criteria=passed,
            failed_criteria=failed,
            message=message,
            done=True,
            reward=reward
        )

    def _unknown_task(self):
        return ScholarshipObservation(
            matched_scholarships=[],
            total_found=0,
            message="Unknown task! Use find_scholarships or find_exams",
            done=True,
            reward=0.0
        )