---
title: Student Opportunity Finder
emoji: 🎓
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
---

# Student Opportunity Finder - OpenEnv Environment

An RL environment that helps Indian students discover scholarships
and government exams they are eligible for.

## What It Does

This environment takes a student profile as input and finds:
- Matching scholarships with eligibility scores and reasons
- Government exams the student can apply for
- Detailed eligibility check for any specific scholarship

## Tasks

### Task 1 - Scholarship Finder (Easy)
Give student profile, get list of matching scholarships with
match scores between 0.0 and 1.0 and detailed reasons.

### Task 2 - Exam Finder (Medium)
Give student profile, get list of government exams with
eligibility details, salary range and age relaxation.

### Task 3 - Eligibility Checker (Hard)
Give student profile and scholarship name, get detailed
pass or fail result for every single eligibility condition.

## Action Space

Student provides:
- name, gender, category, state
- marks_class10, marks_class12
- annual_income, course_level, course_name, age
- task (find_scholarships / find_exams)

## Baseline Scores

- Task 1 Scholarship Finder: 1.0
- Task 2 Exam Finder: 1.0
- Task 3 Eligibility Checker: 1.0
- Average: 1.0

## Setup

pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8000

## Built By

Kartik and Team - DU Students
Meta PyTorch OpenEnv Hackathon 2026