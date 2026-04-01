---
title: Student Opportunity Finder
emoji: "🎓"
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
tags:
  - openenv
  - education
  - scholarships
---

# Student Opportunity Finder

Student Opportunity Finder is a real-world OpenEnv environment for education support. It models a workflow that students, mentors, NGOs, and counseling desks actually perform: finding scholarships, finding government or entrance exams, and checking detailed eligibility for a named program.

## Why This Environment Matters

Students often miss opportunities because rules are fragmented across portals and eligibility conditions are easy to misread. This environment turns that workflow into a structured agent task with:

- typed actions and observations
- partial-progress rewards instead of only binary success
- deterministic graders for three task levels
- a deployable FastAPI plus Docker setup for Hugging Face Spaces

## Tasks

### Task 1: Scholarship Finder

Difficulty: easy

Input a student profile and rank relevant scholarships while filtering out obviously ineligible options.

### Task 2: Exam Finder

Difficulty: medium

Input a student profile and rank relevant government or entrance exams while respecting age, qualification, category relaxation, and course restrictions.

### Task 3: Eligibility Checker

Difficulty: hard

Input a student profile plus an exact scholarship name and return passed criteria, failed criteria, and any missing information that needs manual review.

## OpenEnv Interface

### `POST /reset`

Returns a fresh `EnvironmentState`.

### `POST /step`

Accepts one discriminated action object:

- `task = "find_scholarships"` with `StudentAction`
- `task = "find_exams"` with `StudentAction`
- `task = "check_eligibility"` with `EligibilityAction`

Returns a typed `StepResult`:

- `observation`
- `reward`
- `done`
- `info`

### `GET /state`

Returns the current environment state for the active session.

## Action Space

Core fields:

- `name`
- `gender`
- `category`
- `state`
- `marks_class10`
- `marks_class12`
- `annual_income`
- `course_level`
- `course_name`
- `age`
- `task`

Optional enrichment fields:

- `current_marks`
- `previous_marks`
- `undergraduate_marks`
- `year_of_study`
- `attendance_percentage`
- `study_location`
- `domicile_state`
- `college_type`

Eligibility actions additionally include:

- `scholarship_name`
- nested `student`

## Observation Space

Search tasks return ranked match lists with:

- scholarship or exam metadata
- `match_score`
- `match_reason`

Eligibility returns:

- `passed_criteria`
- `failed_criteria`
- `manual_review_criteria`
- `eligibility_score`

All `step()` calls return a top-level `StepResult` envelope with OpenEnv-style reward and info fields.

## Reward Design

The reward function is shaped across the trajectory:

- scholarship search rewards combine top-match quality with useful coverage
- exam search rewards combine ranking quality with breadth of valid options
- eligibility rewards passed checks and penalize missing required details
- invalid or clearly mismatched options reduce match quality and final reward

This gives a more useful signal than a single end-of-episode success bit.

## Graders

The three graders are deterministic and return scores in `[0.0, 1.0]`.

- `grade_task1()` checks that scholarship recommendations include valid expected matches and exclude invalid ones.
- `grade_task2()` checks that exam recommendations include strong expected options and avoid false positives like `GATE 2026` for a `B.Com` profile.
- `grade_task3()` checks that detailed eligibility catches failure conditions for a scholarship with stricter rules.

## Baseline and Inference

`baseline.py` exercises the local environment directly through HTTP.

`inference.py` is the submission-ready script required by the hackathon. It:

- uses the OpenAI client
- reads `API_BASE_URL`, `MODEL_NAME`, and `HF_TOKEN` or `OPENAI_API_KEY`
- queries the environment task metadata
- asks the model for structured JSON actions
- runs the actions through the environment
- prints task scores and the average

Optional environment variables:

- `ENV_BASE_URL` defaults to `http://localhost:8000`

## Setup

```bash
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000
```

Run local smoke tests:

```bash
python -m unittest test_app.py
python baseline.py
```

Run the inference baseline:

```bash
set API_BASE_URL=https://your-openai-compatible-endpoint
set MODEL_NAME=your-model-name
set HF_TOKEN=your-token
python inference.py
```

## Docker

Build and run:

```bash
docker build -t student-opportunity-finder .
docker run -p 7860:7860 student-opportunity-finder
```

## Hugging Face Space Checklist

Before submission, set these variables in the Space configuration:

- `API_BASE_URL`
- `MODEL_NAME`
- `HF_TOKEN`

Recommended extras:

- `OPENAI_API_KEY` if your provider expects it
- `ENV_BASE_URL` only if `inference.py` should target a non-default environment URL

## Submission Notes

This repo now includes:

- `openenv.yaml`
- `Dockerfile`
- `inference.py`
- deterministic graders
- typed Pydantic actions, observations, and step envelopes
- a working UI and FastAPI app
- `.env.example` for deployment variables
- `.dockerignore` for leaner container builds

## Remaining Improvement Ideas

- add more scholarship-specific rules from `special_conditions`
- expand the dataset and add citation or source links for each scholarship or exam
- add a second hard task focused on multi-step student counseling or recommendation refinement
