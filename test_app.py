import unittest

from fastapi.testclient import TestClient

from app import app
from environment import ScholarshipEnvironment
from models import EligibilityAction, StudentAction


class StudentOpportunityTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.env = ScholarshipEnvironment()

    def test_pragati_does_not_match_non_technical_course(self):
        student = StudentAction(
            name="Asha",
            gender="Female",
            category="General",
            state="Delhi",
            marks_class10=90,
            marks_class12=90,
            annual_income=100000,
            course_level="Undergraduate",
            course_name="B.Sc",
            age=18,
            task="find_scholarships",
        )

        result = self.env.step(student)
        names = [item.name for item in result.observation.matched_scholarships]
        self.assertNotIn("Pragati Scholarship for Girls 2025-26", names)

    def test_gate_does_not_match_bcom_student(self):
        student = StudentAction(
            name="Rohan",
            gender="Male",
            category="General",
            state="Delhi",
            marks_class10=88,
            marks_class12=88,
            annual_income=150000,
            course_level="Undergraduate",
            course_name="B.Com",
            age=22,
            task="find_exams",
        )

        result = self.env.step(student)
        names = [item.name for item in result.observation.matched_exams]
        self.assertNotIn("GATE 2026", names)

    def test_jn_tata_is_not_fully_eligible_for_undergraduate_student(self):
        student = StudentAction(
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
            task="find_scholarships",
        )
        action = EligibilityAction(
            student=student,
            scholarship_name="JN Tata Endowment Loan Scholarship 2026-27",
        )

        result = self.env.step(action).observation
        self.assertFalse(result.is_eligible)
        self.assertTrue(result.failed_criteria or result.manual_review_criteria)

    def test_feedback_requires_reward(self):
        response = self.client.post("/feedback", json={})
        self.assertEqual(response.status_code, 422)

    def test_step_endpoint_returns_openenv_shape(self):
        payload = {
            "task": "find_scholarships",
            "name": "Demo",
            "gender": "Male",
            "category": "General",
            "state": "Delhi",
            "marks_class10": 85,
            "marks_class12": 82,
            "annual_income": 250000,
            "course_level": "Undergraduate",
            "course_name": "B.Sc",
            "age": 18,
        }
        response = self.client.post("/step", json=payload)
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("observation", body)
        self.assertIn("reward", body)
        self.assertIn("done", body)
        self.assertIn("info", body)


if __name__ == "__main__":
    unittest.main()
