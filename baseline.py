import requests

BASE_URL = "http://localhost:8000"

test_student = {
    "name": "Test Student",
    "gender": "Male",
    "category": "General",
    "state": "Delhi",
    "marks_class10": 85.0,
    "marks_class12": 82.0,
    "annual_income": 250000,
    "course_level": "Undergraduate",
    "course_name": "B.Sc",
    "age": 18,
    "task": "find_scholarships"
}

print("=" * 50)
print("BASELINE SCORES")
print("=" * 50)

# Task 1
test_student["task"] = "find_scholarships"
response = requests.post(f"{BASE_URL}/step", json=test_student)
result = response.json()
score1 = result["reward"]
print(f"Task 1 - Scholarship Finder: {score1}")

# Task 2
test_student["task"] = "find_exams"
response = requests.post(f"{BASE_URL}/step", json=test_student)
result = response.json()
score2 = result["reward"]
print(f"Task 2 - Exam Finder: {score2}")

# Task 3
eligibility_data = {
    "student": test_student,
    "scholarship_name": "Buddy4Study ICICI Bank Domestic Education Loan Programme"
}
response = requests.post(f"{BASE_URL}/step/eligibility", json=eligibility_data)
result = response.json()
score3 = result["reward"]
print(f"Task 3 - Eligibility Checker: {score3}")

average = (score1 + score2 + score3) / 3
print(f"\nAverage Score: {average}")
print("=" * 50)