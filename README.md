---
title: Student Opportunity Finder
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Student Opportunity Finder - OpenEnv RL Environment

India's first AI-powered scholarship and government exam finder built as an RL environment.  
Built for the Meta PyTorch OpenEnv Hackathon 2026 by Team DU.

## Live Links

- Live App: https://kartikgod-student-opportunity-finder.hf.space
- API Docs: https://kartikgod-student-opportunity-finder.hf.space/docs
- Baseline: https://kartikgod-student-opportunity-finder.hf.space/baseline
- HuggingFace: https://huggingface.co/spaces/kartikgod/student-opportunity-finder

## What This Does

Millions of Indian students miss scholarships and government exams because they don't know about them. This RL environment trains AI agents to solve that.

Given a student profile, the agent:
- Finds matching scholarships with eligibility scores
- Finds government exams they can apply for
- Checks detailed eligibility for specific scholarships

## Environment Structure

```
Student Profile → ScholarshipEnvironment → Results + Reward
```

Three tasks:
1. Task 1: Scholarship Finder (Easy)
2. Task 2: Exam Finder (Medium)
3. Task 3: Eligibility Check (Hard)

### Task 1 - Scholarship Finder
Give student profile, get ranked scholarships with match scores (0.0-1.0).  
Reward based on quality of matches.

### Task 2 - Government Exam Finder
Give student profile, get list of exams they can apply for.  
Reward based on number of relevant exams.

### Task 3 - Eligibility Checker
Give profile + scholarship name, get pass/fail on each criteria.  
Reward equals eligibility score.

## OpenEnv Interface

Standard 3-method interface:

```python
env.reset()

result = env.step(StudentAction(
    name="Kartik", gender="Male", category="General",
    state="Delhi", marks_class10=85.0, marks_class12=82.0,
    annual_income=250000, course_level="Undergraduate",
    course_name="B.Sc", age=18, task="find_scholarships"
))

result = env.step(StudentAction(..., task="find_exams"))

result = env.step(EligibilityAction(
    student=StudentAction(...),
    scholarship_name="Buddy4Study ICICI Bank Education Loan"
))

state = env.state()
```

## Action Space

StudentAction fields:
- name, gender, category, state
- marks_class10, marks_class12, annual_income
- course_level, course_name, age
- task (find_scholarships or find_exams)

EligibilityAction:
- student (StudentAction object)
- scholarship_name (exact name)

## Observation Space

ScholarshipObservation:
```json
{
  "matched_scholarships": [{
    "name": "Scholarship Name",
    "amount": "50000",
    "deadline": "30-04-2026",
    "match_score": 1.0,
    "match_reason": "Great match! Marks requirement met"
  }],
  "total_found": 5,
  "done": true,
  "reward": 1.0
}
```

EligibilityObservation:
```json
{
  "scholarship_name": "ICICI Bank Loan",
  "is_eligible": true,
  "eligibility_score": 1.0,
  "passed_criteria": ["Gender OK", "Income OK"],
  "done": true,
  "reward": 1.0
}
```

## Baseline Scores

All tasks: 1.0/1.0

Run: `python baseline.py`

## Setup

```bash
git clone https://github.com/kg877253/-student-opportunity-finder.git
cd -student-opportunity-finder
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

Open: http://localhost:8000

## Docker

```bash
docker build -t student-opportunity-finder .
docker run -p 7860:7860 student-opportunity-finder
```

## Data

15 scholarships (Buddy4Study data)  
15 government exams (SSC, UPSC, JEE, NEET, etc)

## Project Structure

```
app.py - FastAPI server
environment.py - RL environment
models.py - Data models
graders.py - Task grading
scholarships_data.py - Scholarship DB
exams_data.py - Exam DB
baseline.py - Baseline script
index.html - UI
```

## Team

**Kartik Gupta** - Lead Dev & RL Environment  
**Aryan Sharma** - UI/UX & Frontend  
**Deepankar Singh** - Data Collection & Testing

1st Year BSc Computer Science  
University of Delhi, India

## License

MIT License

Meta PyTorch OpenEnv Hackathon 2026
