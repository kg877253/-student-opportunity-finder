"""Test if the environment is set up correctly"""

import os
from pathlib import Path

print("=" * 60)
print("CHECKING SETUP")
print("=" * 60)

# Check if index.html exists
if os.path.exists("index.html"):
    print("✅ index.html found!")
    with open("index.html", "r", encoding="utf-8") as f:  # ✅ ADD encoding="utf-8"
        content = f.read()
        if "Student Opportunity Finder" in content:
            print("✅ index.html has correct content!")
else:
    print("❌ index.html NOT found!")
    print("   Current directory:", os.getcwd())
    print("   Files in directory:", os.listdir())

# Check imports
try:
    from app import app
    print("✅ app.py imports correctly!")
except Exception as e:
    print(f"❌ app.py import error: {e}")

try:
    from environment import ScholarshipEnvironment
    print("✅ environment.py imports correctly!")
except Exception as e:
    print(f"❌ environment.py import error: {e}")

try:
    from models import StudentAction
    print("✅ models.py imports correctly!")
except Exception as e:
    print(f"❌ models.py import error: {e}")

try:
    from graders import grade_task1
    print("✅ graders.py imports correctly!")
except Exception as e:
    print(f"❌ graders.py import error: {e}")

print("\n" + "=" * 60)
print("If all ✅, then setup is correct!")
print("=" * 60)