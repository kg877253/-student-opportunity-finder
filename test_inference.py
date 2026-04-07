"""
Quick test to verify inference.py produces structured output
"""
import subprocess
import time
import sys

# Start server
print("Starting server...")
server = subprocess.Popen(
    ["python", "-m", "uvicorn", "app:app", "--host", "127.0.0.1", "--port", "8000"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

time.sleep(5)

try:
    # Run inference
    print("Running inference.py...")
    result = subprocess.run(
        ["python", "inference.py"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print("\n=== STDOUT (structured logs) ===")
    print(result.stdout)
    
    print("\n=== STDERR (debug messages) ===")
    print(result.stderr)
    
    # Check for required output
    stdout = result.stdout
    has_start = "[START]" in stdout
    has_step = "[STEP]" in stdout
    has_end = "[END]" in stdout
    
    print("\n=== VALIDATION ===")
    print(f"Has [START]: {has_start}")
    print(f"Has [STEP]: {has_step}")
    print(f"Has [END]: {has_end}")
    print(f"Exit code: {result.returncode}")
    
    if has_start and has_step and has_end and result.returncode == 0:
        print("\n✓ ALL CHECKS PASSED!")
        sys.exit(0)
    else:
        print("\n✗ VALIDATION FAILED")
        sys.exit(1)
        
finally:
    print("\nStopping server...")
    server.terminate()
    server.wait()
