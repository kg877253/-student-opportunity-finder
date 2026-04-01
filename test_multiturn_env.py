import unittest

from fastapi.testclient import TestClient

from app import app
from multiturn_environment import MultiTurnScholarshipGuidanceEnvironment


class MultiTurnEnvironmentTests(unittest.TestCase):
    def setUp(self):
        self.env = MultiTurnScholarshipGuidanceEnvironment()
        self.client = TestClient(app)

    def test_reset_hides_profile_fields(self):
        observation = self.env.reset("easy_scholarship_shortlist")
        self.assertIn("annual_income", observation.missing_fields)
        self.assertIsNone(observation.revealed_profile["annual_income"])
        self.assertFalse(observation.done)

    def test_asking_critical_field_reveals_it_and_rewards_agent(self):
        self.env.reset("easy_scholarship_shortlist")
        result = self.env.step({"action_type": "ask_profile_field", "field_name": "annual_income"})
        self.assertGreater(result.reward, 0)
        self.assertEqual(result.observation.revealed_profile["annual_income"], 200000)
        self.assertNotIn("annual_income", result.observation.missing_fields)

    def test_repeating_same_field_is_penalized(self):
        self.env.reset("easy_scholarship_shortlist")
        self.env.step({"action_type": "ask_profile_field", "field_name": "annual_income"})
        result = self.env.step({"action_type": "ask_profile_field", "field_name": "annual_income"})
        self.assertLess(result.reward, 0)

    def test_good_finalization_finishes_episode(self):
        self.env.reset("hard_mixed_guidance")
        state = self.env.state_snapshot()
        for field_name in state.critical_fields:
            self.env.step({"action_type": "ask_profile_field", "field_name": field_name})
        state = self.env.state_snapshot()
        result = self.env.step(
            {
                "action_type": "finalize_guidance",
                "scholarship_names": state.target_scholarships,
                "exam_names": state.target_exams,
                "primary_scholarship": state.primary_scholarship,
            }
        )
        self.assertTrue(result.done)
        self.assertGreater(result.reward, 0.5)

    def test_multiturn_app_baseline_endpoint_returns_scores(self):
        response = self.client.get("/rl/baseline")
        body = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIn("average_score", body)


if __name__ == "__main__":
    unittest.main()
