"""
Local Test Script for inference.py
Run this BEFORE submitting to catch issues early!
"""
import subprocess
import sys
import time
import os

# Use the virtual environment python if available
venv_python = os.path.join(os.path.dirname(__file__), ".venv", "Scripts", "python.exe")
if not os.path.exists(venv_python):
    venv_python = sys.executable

print("="*70)
print("LOCAL INFERENCE.PY TEST")
print("="*70)
print(f"Using Python: {venv_python}")

# Step 1: Start the server
print("\n[1/4] Starting environment server...")
server = subprocess.Popen(
    [venv_python, "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    cwd=os.path.dirname(os.path.abspath(__file__))
)

print("Waiting 10 seconds for server to start...")
time.sleep(10)

try:
    # Step 2: Set environment variables (simulate judge environment)
    print("\n[2/4] Setting environment variables...")
    test_env = os.environ.copy()
    test_env["ENV_BASE_URL"] = "http://127.0.0.1:8000"
    test_env["API_BASE_URL"] = "https://api.openai.com/v1"  # Mock - won't actually call
    test_env["MODEL_NAME"] = "gpt-4"
    test_env["API_KEY"] = "test-key-12345"  # Mock key for testing
    print("  ENV_BASE_URL: http://127.0.0.1:8000")
    print("  API_BASE_URL: https://api.openai.com/v1")
    print("  MODEL_NAME: gpt-4")
    print("  API_KEY: test-key-***** (set)")
    
    # Step 3: Run inference.py
    print("\n[3/4] Running inference.py...")
    print("-" * 70)
    
    result = subprocess.run(
        [venv_python, "inference.py"],
        capture_output=True,
        text=True,
        timeout=180,  # 3 minutes max
        env=test_env,
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    
    # Step 4: Check results
    print("\n[4/4] Checking results...")
    print("="*70)
    
    stdout = result.stdout
    stderr = result.stderr
    
    # Count structured logs
    start_count = stdout.count("[START]")
    step_count = stdout.count("[STEP]")
    end_count = stdout.count("[END]")
    
    print(f"\nExit Code: {result.returncode}")
    print(f"[START] logs: {start_count}/3")
    print(f"[STEP] logs: {step_count}/3")
    print(f"[END] logs: {end_count}/3")
    
    # Show first 800 chars of output
    print(f"\nSTDOUT (first 800 chars):")
    print("-" * 70)
    print(stdout[:800] if stdout else "(empty)")
    
    # Show stderr
    print(f"\nSTDERR:")
    print("-" * 70)
    print(stderr[:500] if stderr else "(empty)")
    
    # Final verdict
    print("\n" + "="*70)
    if result.returncode == 0 and start_count == 3 and step_count == 3 and end_count == 3:
        print(">>> TEST PASSED <<<")
        print("Your inference.py is working correctly!")
        print("Safe to submit to the hackathon.")
    else:
        print(">>> TEST FAILED <<<")
        print("\nIssues found:")
        if result.returncode != 0:
            print(f"  - Non-zero exit code: {result.returncode}")
        if start_count != 3:
            print(f"  - Wrong number of [START] logs: {start_count} (expected 3)")
        if step_count != 3:
            print(f"  - Wrong number of [STEP] logs: {step_count} (expected 3)")
        if end_count != 3:
            print(f"  - Wrong number of [END] logs: {end_count} (expected 3)")
        print("\nFIX THESE BEFORE SUBMITTING!")
    print("="*70)
    
    sys.exit(0 if result.returncode == 0 and start_count == 3 else 1)

finally:
    # Cleanup
    print("\nCleaning up...")
    server.terminate()
    server.wait(timeout=5)
    print("Server stopped.")
