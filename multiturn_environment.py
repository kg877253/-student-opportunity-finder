import uuid

from environment import ScholarshipEnvironment
from exams_data import exams
from models import EligibilityAction, StudentAction
from pydantic import TypeAdapter
from scholarships_data import scholarships

from multiturn_models import (
    AskProfileFieldAction,
    DraftGuidanceAction,
    FinalizeGuidanceAction,
    GuidanceEnvironmentState,
    GuidanceInfo,
    GuidanceObservation,
    GuidanceStepResult,
    MultiTurnAction,
    MultiTurnTaskName,
    ProfileField,
)


TASK_LIBRARY: dict[MultiTurnTaskName, dict] = {
    "easy_scholarship_shortlist": {
        "difficulty": "easy",
        "guidance_mode": "scholarship",
        "goal": (
            "Ask for the most important missing student details, then finalize the best scholarships "
            "for a first-year engineering student."
        ),
        "student_profile": {
            "name": "Asha",
            "gender": "Female",
            "category": "General",
            "state": "Delhi",
            "marks_class10": 92,
            "marks_class12": 91,
            "annual_income": 200000,
            "course_level": "Undergraduate",
            "course_name": "B.Tech",
            "age": 18,
            "current_marks": 74,
            "year_of_study": 1,
            "study_location": "India",
            "college_type": "NIRF ranked",
            "domicile_state": "Delhi",
        },
        "initial_revealed_fields": [
            "gender",
            "state",
            "marks_class12",
            "course_level",
            "course_name",
            "age",
        ],
        "critical_fields": ["annual_income", "current_marks", "year_of_study", "college_type"],
        "max_steps": 5,
        "target_scholarship_count": 3,
        "target_exam_count": 0,
        "preferred_scholarships": [
            "Vivo KanyaGyaan Scholarship Program 2025-26",
            "Pragati Scholarship for Girls 2025-26",
            "Buddy4Study ICICI Bank Domestic Education Loan Programme",
        ],
        "preferred_exams": [],
        "preferred_primary_scholarship": "Vivo KanyaGyaan Scholarship Program 2025-26",
        "forbidden_scholarships": ["JN Tata Endowment Loan Scholarship 2026-27"],
        "forbidden_exams": [],
    },
    "medium_exam_guidance": {
        "difficulty": "medium",
        "guidance_mode": "exam",
        "goal": (
            "Recover the missing age, qualification, and state context, then finalize the strongest exam "
            "options for a commerce student without wasting turns."
        ),
        "student_profile": {
            "name": "Rohan",
            "gender": "Male",
            "category": "OBC",
            "state": "Delhi",
            "marks_class10": 86,
            "marks_class12": 84,
            "annual_income": 300000,
            "course_level": "Graduation",
            "course_name": "B.Com",
            "age": 24,
            "study_location": "India",
        },
        "initial_revealed_fields": ["gender", "marks_class12", "course_name"],
        "critical_fields": ["age", "course_level", "state", "category"],
        "max_steps": 6,
        "target_scholarship_count": 0,
        "target_exam_count": 4,
        "preferred_scholarships": [],
        "preferred_exams": [
            "IBPS Clerk 2025",
            "SBI PO 2025",
            "SSC CGL 2025",
            "IBPS PO 2025",
        ],
        "preferred_primary_scholarship": None,
        "forbidden_scholarships": [],
        "forbidden_exams": ["GATE 2026", "NDA 2025"],
    },
    "hard_mixed_guidance": {
        "difficulty": "hard",
        "guidance_mode": "mixed",
        "goal": (
            "With a tight turn budget, discover the missing scholarship-critical details for a high-performing "
            "SC engineering student, avoid tempting ineligible options, and finalize a mixed guidance plan."
        ),
        "student_profile": {
            "name": "Sana",
            "gender": "Female",
            "category": "SC",
            "state": "Karnataka",
            "marks_class10": 88,
            "marks_class12": 89,
            "annual_income": 180000,
            "course_level": "Undergraduate",
            "course_name": "B.Tech",
            "age": 19,
            "current_marks": 81,
            "year_of_study": 1,
            "study_location": "India",
            "college_type": "NIRF ranked",
            "domicile_state": "Karnataka",
        },
        "initial_revealed_fields": ["gender", "category", "course_level", "course_name", "marks_class12"],
        "critical_fields": ["annual_income", "current_marks", "year_of_study", "college_type", "study_location", "age"],
        "max_steps": 7,
        "target_scholarship_count": 3,
        "target_exam_count": 1,
        "preferred_scholarships": [
            "Vivo KanyaGyaan Scholarship Program 2025-26",
            "Infosys Foundation SC ST Technology Scholarship 2025-26",
            "Post Matric Scholarship for SC Students 2025-26",
        ],
        "preferred_exams": ["GATE 2026"],
        "preferred_primary_scholarship": "Vivo KanyaGyaan Scholarship Program 2025-26",
        "forbidden_scholarships": ["JN Tata Endowment Loan Scholarship 2026-27"],
        "forbidden_exams": ["NDA 2025"],
    },
}


class MultiTurnScholarshipGuidanceEnvironment:
    def __init__(self):
        self.scoring_env = ScholarshipEnvironment()
        self._scenario: dict | None = None
        self.state: GuidanceEnvironmentState | None = None
        self._log: list[str] = []
        self._action_adapter = TypeAdapter(MultiTurnAction)
        self.reset()

    def reset(self, task_name: MultiTurnTaskName = "easy_scholarship_shortlist") -> GuidanceObservation:
        scenario = TASK_LIBRARY[task_name]
        student_profile = dict(scenario["student_profile"])
        revealed_fields = list(scenario["initial_revealed_fields"])
        missing_fields = [field for field in student_profile if field not in revealed_fields and field != "name"]

        targets = self._build_reference_guidance(student_profile, scenario)
        self._scenario = scenario
        self._log = [
            "Episode reset.",
            f"Goal: {scenario['goal']}",
            f"Start by revealing the most informative hidden fields. Turn budget: {scenario['max_steps']}.",
        ]
        self.state = GuidanceEnvironmentState(
            episode_id=str(uuid.uuid4()),
            task_name=task_name,
            difficulty=scenario["difficulty"],
            guidance_mode=scenario["guidance_mode"],
            step_count=0,
            max_steps=scenario["max_steps"],
            total_reward=0.0,
            done=False,
            revealed_fields=revealed_fields,
            missing_fields=missing_fields,
            critical_fields=list(scenario["critical_fields"]),
            draft_scholarships=[],
            draft_exams=[],
            full_student_profile=student_profile,
            target_scholarships=targets["target_scholarships"],
            target_exams=targets["target_exams"],
            primary_scholarship=targets["primary_scholarship"],
            forbidden_scholarships=list(scenario["forbidden_scholarships"]),
            forbidden_exams=list(scenario["forbidden_exams"]),
        )
        return self._build_observation("Episode reset. Some student fields are hidden.", reward=0.0)

    def state_snapshot(self) -> GuidanceEnvironmentState:
        if self.state is None:
            self.reset()
        return self.state

    def step(self, action: MultiTurnAction | dict) -> GuidanceStepResult:
        if self.state is None:
            initial_observation = self.reset()
            return self._step_result(initial_observation)
        if self.state.done:
            observation = self._build_observation(
                "Episode already finished. Call reset() to start a new one.",
                reward=-0.05,
                extra_messages=["No more actions are accepted after finalize or turn limit."],
            )
            return self._step_result(observation, notes=["episode_finished"])

        if isinstance(action, dict):
            action = self._action_adapter.validate_python(action)

        self.state.step_count += 1
        notes: list[str] = []

        if isinstance(action, AskProfileFieldAction):
            observation = self._handle_ask_profile_field(action)
        elif isinstance(action, DraftGuidanceAction):
            observation = self._handle_draft_guidance(action)
        elif isinstance(action, FinalizeGuidanceAction):
            observation = self._handle_finalize_guidance(action)
        else:
            observation = self._build_observation(
                "Unknown action. Choose ask_profile_field, draft_guidance, or finalize_guidance.",
                reward=-0.1,
            )
            notes.append("unknown_action")

        if not self.state.done and self.state.step_count >= self.state.max_steps:
            self.state.done = True
            overtime_penalty = max(-1.0, round(observation.reward - 0.15, 2))
            self.state.total_reward = round(self.state.total_reward - 0.15, 2)
            observation = self._build_observation(
                "Turn limit reached before a confident final answer.",
                reward=overtime_penalty,
                extra_messages=["The episode ended because the step budget was exhausted."],
            )
            notes.append("turn_limit_reached")

        return self._step_result(observation, notes=notes)

    def _handle_ask_profile_field(self, action: AskProfileFieldAction) -> GuidanceObservation:
        assert self.state is not None
        field_name = action.field_name
        if field_name in self.state.revealed_fields:
            self.state.total_reward = round(self.state.total_reward - 0.08, 2)
            self._log.append(f"Repeated question about {field_name}.")
            return self._build_observation(
                f"{field_name} was already revealed, so this turn was wasted.",
                reward=-0.08,
            )

        if field_name not in self.state.full_student_profile:
            self.state.total_reward = round(self.state.total_reward - 0.1, 2)
            self._log.append(f"Asked for unsupported field {field_name}.")
            return self._build_observation(
                f"{field_name} is not part of this environment profile.",
                reward=-0.1,
            )

        self.state.revealed_fields.append(field_name)
        self.state.revealed_fields = sorted(set(self.state.revealed_fields))
        self.state.missing_fields = [field for field in self.state.missing_fields if field != field_name]

        reward = 0.12 if field_name in self.state.critical_fields else 0.05
        self.state.total_reward = round(self.state.total_reward + reward, 2)
        value = self.state.full_student_profile[field_name]
        self._log.append(f"Revealed {field_name}: {value}")
        return self._build_observation(
            f"Revealed {field_name}: {value}",
            reward=reward,
        )

    def _handle_draft_guidance(self, action: DraftGuidanceAction) -> GuidanceObservation:
        assert self.state is not None
        self.state.draft_scholarships = action.scholarship_names[:]
        self.state.draft_exams = action.exam_names[:]

        reward, messages = self._score_guidance_submission(
            scholarship_names=action.scholarship_names,
            exam_names=action.exam_names,
            primary_scholarship=None,
            final=False,
        )
        self.state.total_reward = round(self.state.total_reward + reward, 2)
        self._log.extend(messages)
        return self._build_observation(
            "Draft guidance received. Use the feedback to improve before finalizing.",
            reward=reward,
            extra_messages=messages,
        )

    def _handle_finalize_guidance(self, action: FinalizeGuidanceAction) -> GuidanceObservation:
        assert self.state is not None
        self.state.draft_scholarships = action.scholarship_names[:]
        self.state.draft_exams = action.exam_names[:]

        reward, messages = self._score_guidance_submission(
            scholarship_names=action.scholarship_names,
            exam_names=action.exam_names,
            primary_scholarship=action.primary_scholarship,
            final=True,
        )
        self.state.done = True
        self.state.total_reward = round(self.state.total_reward + reward, 2)
        self._log.extend(messages)
        return self._build_observation(
            "Final guidance submitted. Episode finished.",
            reward=reward,
            extra_messages=messages,
        )

    def _score_guidance_submission(
        self,
        scholarship_names: list[str],
        exam_names: list[str],
        primary_scholarship: str | None,
        final: bool,
    ) -> tuple[float, list[str]]:
        assert self.state is not None
        scholarship_score = self._ranked_overlap(
            proposed=scholarship_names,
            expected=self.state.target_scholarships,
            forbidden=self.state.forbidden_scholarships,
        )
        exam_score = self._ranked_overlap(
            proposed=exam_names,
            expected=self.state.target_exams,
            forbidden=self.state.forbidden_exams,
        )
        info_completeness = self._information_completeness()
        efficiency = (self.state.max_steps - self.state.step_count) / self.state.max_steps
        guidance_mode = self.state.guidance_mode

        if guidance_mode == "scholarship":
            recommendation_score = scholarship_score
        elif guidance_mode == "exam":
            recommendation_score = exam_score
        else:
            recommendation_score = round((0.65 * scholarship_score) + (0.35 * exam_score), 2)

        primary_score = 0.0
        if self.state.primary_scholarship:
            if primary_scholarship and self._normalize(primary_scholarship) == self._normalize(self.state.primary_scholarship):
                primary_score = 1.0
            elif primary_scholarship:
                primary_score = 0.0
            else:
                primary_score = 0.2
        elif primary_scholarship:
            primary_score = 0.4

        if final:
            reward = (
                0.55 * recommendation_score
                + 0.2 * primary_score
                + 0.15 * info_completeness
                + 0.1 * max(0.0, efficiency)
            )
            if not scholarship_names and not exam_names:
                reward -= 0.25
            if self.state.critical_fields and self._critical_missing_fields():
                reward -= 0.05 * len(self._critical_missing_fields())
        else:
            reward = 0.45 * recommendation_score + 0.2 * info_completeness
            if not scholarship_names and not exam_names:
                reward = -0.05

        reward = round(max(-1.0, min(1.0, reward)), 2)
        messages = [
            f"Scholarship shortlist score: {scholarship_score:.2f}",
            f"Exam shortlist score: {exam_score:.2f}",
            f"Information completeness: {info_completeness:.2f}",
        ]
        if self.state.primary_scholarship:
            messages.append(f"Primary scholarship target for this task: {self.state.primary_scholarship}")
        if final:
            messages.append("Finalization rewards accuracy, completeness, and efficiency together.")
        return reward, messages

    def _information_completeness(self) -> float:
        assert self.state is not None
        if not self.state.critical_fields:
            return 1.0
        known = sum(1 for field in self.state.critical_fields if field in self.state.revealed_fields)
        return round(known / len(self.state.critical_fields), 2)

    def _critical_missing_fields(self) -> list[ProfileField]:
        assert self.state is not None
        return [field for field in self.state.critical_fields if field not in self.state.revealed_fields]

    def _ranked_overlap(self, proposed: list[str], expected: list[str], forbidden: list[str]) -> float:
        normalized_proposed = [self._normalize(item) for item in proposed]
        normalized_expected = [self._normalize(item) for item in expected]
        normalized_forbidden = {self._normalize(item) for item in forbidden}

        if not expected:
            base = 1.0 if not proposed else max(0.0, 1.0 - (0.25 * len(proposed)))
        else:
            hits = 0
            weighted_hits = 0.0
            for index, name in enumerate(normalized_expected, start=1):
                if name in normalized_proposed:
                    hits += 1
                    weighted_hits += 1 / index
            precision = hits / len(proposed) if proposed else 0.0
            recall = hits / len(expected)
            order_bonus = 0.15 if proposed and expected and normalized_proposed[:1] == normalized_expected[:1] else 0.0
            weighted_recall = weighted_hits / sum(1 / i for i in range(1, len(normalized_expected) + 1))
            base = (0.35 * precision) + (0.4 * recall) + (0.25 * weighted_recall) + order_bonus

        forbidden_hits = sum(1 for item in normalized_proposed if item in normalized_forbidden)
        penalty = 0.3 * forbidden_hits
        return round(max(0.0, min(1.0, base - penalty)), 2)

    def _build_reference_guidance(self, student_profile: dict, scenario: dict) -> dict[str, list[str] | str | None]:
        scholarships_ranked = self._rank_scholarships(student_profile)
        exams_ranked = self._rank_exams(student_profile)

        target_scholarships = [
            item["name"]
            for item in scholarships_ranked
            if item["score"] >= 0.55 and item["name"] not in scenario["forbidden_scholarships"]
        ][: scenario["target_scholarship_count"]]
        target_exams = [
            item["name"]
            for item in exams_ranked
            if item["score"] >= 0.55 and item["name"] not in scenario["forbidden_exams"]
        ][: scenario["target_exam_count"]]

        target_scholarships = self._prefer_named_targets(
            ranked_items=scholarships_ranked,
            default_targets=target_scholarships,
            preferred_targets=scenario.get("preferred_scholarships", []),
            forbidden_targets=scenario["forbidden_scholarships"],
            limit=scenario["target_scholarship_count"],
        )
        target_exams = self._prefer_named_targets(
            ranked_items=exams_ranked,
            default_targets=target_exams,
            preferred_targets=scenario.get("preferred_exams", []),
            forbidden_targets=scenario["forbidden_exams"],
            limit=scenario["target_exam_count"],
        )

        primary_scholarship = self._best_eligible_scholarship(student_profile, target_scholarships)
        preferred_primary = scenario.get("preferred_primary_scholarship")
        if preferred_primary and preferred_primary in target_scholarships:
            primary_scholarship = preferred_primary
        if primary_scholarship is None and target_scholarships:
            primary_scholarship = target_scholarships[0]

        return {
            "target_scholarships": target_scholarships,
            "target_exams": target_exams,
            "primary_scholarship": primary_scholarship,
        }

    def _prefer_named_targets(
        self,
        ranked_items: list[dict],
        default_targets: list[str],
        preferred_targets: list[str],
        forbidden_targets: list[str],
        limit: int,
    ) -> list[str]:
        if limit == 0:
            return []

        normalized_forbidden = {self._normalize(item) for item in forbidden_targets}
        ranked_by_name = {item["name"]: item for item in ranked_items}
        selected: list[str] = []

        for item_name in preferred_targets:
            ranked_item = ranked_by_name.get(item_name)
            if ranked_item and ranked_item["score"] >= 0.5 and self._normalize(item_name) not in normalized_forbidden:
                selected.append(item_name)

        for item_name in default_targets:
            if item_name not in selected:
                selected.append(item_name)

        return selected[:limit]

    def _rank_scholarships(self, student_profile: dict) -> list[dict]:
        action = StudentAction(task="find_scholarships", **student_profile)
        ranked = []
        for scholarship in scholarships:
            score, reason = self.scoring_env._calculate_scholarship_match(action, scholarship)
            ranked.append({"name": scholarship["name"], "score": round(score, 2), "reason": reason})
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked

    def _rank_exams(self, student_profile: dict) -> list[dict]:
        action = StudentAction(task="find_exams", **student_profile)
        ranked = []
        for exam in exams:
            score, reason, _ = self.scoring_env._calculate_exam_match(action, exam)
            ranked.append({"name": exam["name"], "score": round(score, 2), "reason": reason})
        ranked.sort(key=lambda item: item["score"], reverse=True)
        return ranked

    def _best_eligible_scholarship(self, student_profile: dict, candidate_names: list[str]) -> str | None:
        for scholarship_name in candidate_names:
            action = EligibilityAction(
                student=StudentAction(task="find_scholarships", **student_profile),
                scholarship_name=scholarship_name,
            )
            result = self.scoring_env._check_eligibility(action)
            if result.is_eligible:
                return scholarship_name
        return None

    def _build_observation(
        self,
        summary: str,
        reward: float,
        extra_messages: list[str] | None = None,
    ) -> GuidanceObservation:
        assert self.state is not None
        revealed_profile = {
            key: self.state.full_student_profile.get(key) if key in self.state.revealed_fields or key == "name" else None
            for key in self.state.full_student_profile
        }
        messages = [
            f"Critical fields still hidden: {', '.join(self._critical_missing_fields()) or 'none'}",
            f"Current draft scholarships: {', '.join(self.state.draft_scholarships) or 'none'}",
            f"Current draft exams: {', '.join(self.state.draft_exams) or 'none'}",
        ]
        if extra_messages:
            messages.extend(extra_messages)

        return GuidanceObservation(
            task_name=self.state.task_name,
            difficulty=self.state.difficulty,
            guidance_mode=self.state.guidance_mode,
            goal=self._scenario["goal"],
            revealed_profile=revealed_profile,
            missing_fields=list(self.state.missing_fields),
            critical_missing_fields=self._critical_missing_fields(),
            remaining_steps=max(0, self.state.max_steps - self.state.step_count),
            last_action_summary=summary,
            draft_scholarships=self.state.draft_scholarships,
            draft_exams=self.state.draft_exams,
            guidance_messages=messages,
            available_actions=["ask_profile_field", "draft_guidance", "finalize_guidance"],
            done=self.state.done,
            reward=round(reward, 2),
        )

    def _step_result(self, observation: GuidanceObservation, notes: list[str] | None = None) -> GuidanceStepResult:
        assert self.state is not None
        return GuidanceStepResult(
            observation=observation,
            reward=observation.reward,
            done=observation.done,
            info=GuidanceInfo(
                episode_id=self.state.episode_id,
                task_name=self.state.task_name,
                step_count=self.state.step_count,
                max_steps=self.state.max_steps,
                total_reward=round(self.state.total_reward, 2),
                notes=notes or [],
            ),
        )

    def _normalize(self, value) -> str:
        return str(value).strip().lower()
