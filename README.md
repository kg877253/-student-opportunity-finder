# 🚀 AI-Powered Student Opportunity Recommender

An intelligent RL-based environment that helps Indian students discover
**scholarships** and **government exams** they are eligible for.

---

## 🌍 Problem Statement

Millions of Indian students miss out on scholarships and government
opportunities due to lack of awareness and complex eligibility criteria.

This project solves that by:
- Matching students with relevant scholarships
- Suggesting government exams based on eligibility
- Providing detailed eligibility breakdown

---

## 🧠 Solution Approach

We built a **Reinforcement Learning-based environment** where:

- The **agent** decides whether to recommend:
  - Scholarships OR
  - Government Exams

- The system evaluates:
  - Academic performance
  - Income level
  - Category (OBC/SC/ST/etc)
  - Age and course

- The agent improves over time using **reward signals**

---

## ⚙️ System Flow
User Input → FastAPI → Environment → Matching Logic → Result → Reward → Learning

---

## 📌 Features

✅ Scholarship Recommendation  
✅ Government Exam Finder  
✅ Eligibility Checker (detailed pass/fail)  
✅ Reinforcement Learning integration  
✅ Dockerized deployment  
✅ Baseline scoring system  

---

## 🧪 Example Input

```json
{
  "name": "Kartik",
  "gender": "Male",
  "category": "OBC",
  "state": "Delhi",
  "marks_class10": 85,
  "marks_class12": 88,
  "annual_income": 200000,
  "course_level": "Undergraduate",
  "course_name": "B.Sc",
  "age": 18,
  "task": "find_scholarships"
}
Scholarship Matches:

1. XYZ Scholarship → Match Score: 0.9
   ✔ Income criteria satisfied
   ✔ Marks above threshold

2. ABC Scholarship → Match Score: 0.6
   ✔ Marks satisfied
   ❌ Income slightly above limit
