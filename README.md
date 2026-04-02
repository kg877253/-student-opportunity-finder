---
title: Student Opportunity Finder
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# 🎓 Student Opportunity Finder — OpenEnv RL Environment

> **India's first AI-powered scholarship and government exam finder built as an RL environment**
> Built for the **Meta PyTorch OpenEnv Hackathon 2026** by Team DU

---

## 🌐 Live Links

| Resource | Link |
|---|---|
| 🚀 Live App (Student UI) | [Open App](https://kartikgod-student-opportunity-finder.hf.space) |
| 📖 API Documentation | [Open Docs](https://kartikgod-student-opportunity-finder.hf.space/docs) |
| 📊 Baseline Scores | [View Scores](https://kartikgod-student-opportunity-finder.hf.space/baseline) |
| 🤗 HuggingFace Space | [Open Space](https://huggingface.co/spaces/kartikgod/student-opportunity-finder) |

---

## 🎯 What This Environment Does

Millions of Indian students miss out on scholarships and government exam opportunities simply because they don't know about them. This RL environment trains AI agents to solve that problem!

Given a student's profile, the AI agent:
- Finds matching scholarships with eligibility scores and detailed reasons
- Finds government exams the student can apply for
- Checks detailed eligibility for any specific scholarship

---

## 🏗️ Environment Architecture

```
Student Profile (Action)
        ↓
ScholarshipEnvironment
        ↓
    ┌─────────────────────────────┐
    │  Task 1: Scholarship Finder │  ← Easy
    │  Task 2: Exam Finder        │  ← Medium  
    │  Task 3: Eligibility Check  │  ← Hard
    └─────────────────────────────┘
        ↓
Matched Results + Reward (0.0 → 1.0)
```

---

## 📋 3 Tasks

### Task 1 — Scholarship Finder (Easy) 🎓
Give a student profile, get a ranked list of matching scholarships with match scores between 0.0 and 1.0 and detailed reasons for each match.

**Reward:** Based on number and quality of matches found (0.0 to 1.0)

### Task 2 — Government Exam Finder (Medium) 📋
Give a student profile, get a list of government exams the student can apply for — with eligibility details, salary range and category-wise age relaxation.

**Reward:** Based on number of relevant exams found (0.0 to 1.0)

### Task 3 — Eligibility Checker (Hard) ✅
Give a student profile and a specific scholarship name. Get a detailed pass/fail result for every single eligibility condition — gender, state, category, marks, income and age.

**Reward:** Directly equals the eligibility score (0.0 to 1.0)

---

## 🎮 OpenEnv Interface

Every task uses the standard 3-method OpenEnv interface:

```python
# Reset environment
env.reset()

# Task 1 - Find Scholarships
result = env.step(StudentAction(
    name="Kartik",
    gender="Male",
    category="General",
    state="Delhi",
    marks_class10=85.0,
    marks_class12=82.0,
    annual_income=250000,
    course_level="Undergraduate",
    course_name="B.Sc",
    age=18,
    task="find_scholarships"
))

# Task 2 - Find Exams
result = env.step(StudentAction(..., task="find_exams"))

# Task 3 - Check Eligibility
result = env.step(EligibilityAction(
    student=StudentAction(...),
    scholarship_name="Buddy4Study ICICI Bank Domestic Education Loan Programme"
))

# Get state
state = env.state()
```

---

## 📥 Action Space

**StudentAction** (for Task 1 and Task 2):

| Field | Type | Description |
|---|---|---|
| name | string | Student's name |
| gender | string | Male or Female |
| category | string | General, OBC, SC, ST or Minority |
| state | string | Like Delhi, Maharashtra etc |
| marks_class10 | float | Class 10 percentage |
| marks_class12 | float | Class 12 percentage |
| annual_income | float | Annual family income in rupees |
| course_level | string | Undergraduate or Postgraduate |
| course_name | string | Like B.Sc, B.Tech etc |
| age | integer | Student's age |
| task | string | find_scholarships or find_exams |

**EligibilityAction** (for Task 3):

| Field | Type | Description |
|---|---|---|
| student | StudentAction | Complete student profile |
| scholarship_name | string | Exact scholarship name to check |

---

## 📤 Observation Space

**ScholarshipObservation** (Task 1):
```json
{
  "matched_scholarships": [
    {
      "name": "Scholarship Name",
      "amount": "50000",
      "deadline": "30-04-2026",
      "match_score": 1.0,
      "match_reason": "Great match! Your marks meet the requirement..."
    }
  ],
  "total_found": 5,
  "message": "Found 5 scholarships for you!",
  "done": true,
  "reward": 1.0
}
```

**EligibilityObservation** (Task 3):
```json
{
  "scholarship_name": "ICICI Bank Education Loan",
  "is_eligible": true,
  "eligibility_score": 1.0,
  "passed_criteria": ["Gender: Male is accepted", "..."],
  "failed_criteria": [],
  "message": "Congratulations! You are eligible!",
  "done": true,
  "reward": 1.0
}
```

---

## 📊 Baseline Scores

| Task | Description | Score |
|---|---|---|
| Task 1 | Scholarship Finder | **1.0 / 1.0** |
| Task 2 | Exam Finder | **1.0 / 1.0** |
| Task 3 | Eligibility Checker | **1.0 / 1.0** |
| **Average** | **All Tasks** | **1.0 / 1.0** |

Run baseline yourself:
```bash
python baseline.py
```

---

## 🚀 Setup and Run Locally

**Step 1 — Clone the repo:**
```bash
git clone https://github.com/kg877253/-student-opportunity-finder.git
cd -student-opportunity-finder
```

**Step 2 — Install dependencies:**
```bash
pip install -r requirements.txt
```

**Step 3 — Run the server:**
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

**Step 4 — Open in browser:**
```
http://localhost:8000        ← Student UI
http://localhost:8000/docs   ← API Documentation
http://localhost:8000/baseline ← Baseline Scores
```

---

## 🐳 Run with Docker

```bash
docker build -t student-opportunity-finder .
docker run -p 7860:7860 student-opportunity-finder
```

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | / | Student UI homepage |
| GET | /health | Health check |
| POST | /reset | Reset environment |
| POST | /step | Find scholarships or exams |
| POST | /step/eligibility | Check eligibility |
| GET | /state | Get current state |
| GET | /tasks | List all tasks |
| GET | /baseline | Baseline scores |
| GET | /grader | Grader scores |
| GET | /docs | API documentation |

---

## 📚 Data

**Scholarships (15 total):**
- Real data from Buddy4Study
- Covers General, OBC, SC, ST, Minority categories
- Covers all India and state-specific scholarships
- Merit, need-based, loan and sports scholarships

**Government Exams (15 total):**
- SSC CGL, UPSC, NDA, IBPS PO, SBI PO
- JEE Main, NEET, CUET, GATE
- Delhi Police, DSSSB, RRB NTPC and more

---

## 🏆 Reward Function

```python
# Partial rewards throughout episode
reward = min(1.0, matched_count / threshold)

# Eligibility reward = exact eligibility score
reward = passed_criteria / total_criteria
```

Rewards are never binary — always partial progress signals!

---

## 📁 Project Structure

```
student-opportunity-finder/
├── app.py                 ← FastAPI server
├── environment.py         ← Core RL environment
├── models.py              ← Pydantic data models
├── graders.py             ← Task graders (0.0 to 1.0)
├── scholarships_data.py   ← Scholarship database
├── exams_data.py          ← Exam database
├── baseline.py            ← Baseline inference script
├── index.html             ← Student-facing UI
├── Dockerfile             ← Container definition
├── requirements.txt       ← Dependencies
└── openenv.yaml           ← OpenEnv metadata
```

---

## 👥 Built By

| Name | Role | College |
|---|---|---|
| Kartik Gupta | Lead Developer | Delhi University |
| Team Member 2 | Exam Finder Module | Delhi University |
| Team Member 3 | Testing and Deployment | Delhi University |

**1st Year BSc Physical Science with Computer Science**
**University of Delhi, India 🇮🇳**

---

## 💡 Real World Impact

This environment addresses a genuine problem — millions of Indian students from small towns and villages miss life-changing scholarship opportunities simply because they don't have access to the right information. Our AI agent learns to bridge this gap!

---

## 📜 License

MIT License — Free to use, modify and distribute!

---

*Built with ❤️ for India | Meta PyTorch OpenEnv Hackathon 2026*
