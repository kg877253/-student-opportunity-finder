# How to Test inference.py Locally

**BEFORE submitting to the hackathon, always test locally!**

## Quick Test (Recommended)

```bash
python test_local.py
```

This script will:
1. Start your environment server
2. Run inference.py
3. Verify all required [START]/[STEP]/[END] logs appear
4. Show you if it passed or failed

**If you see "TEST PASSED" - you're good to submit!**

## Manual Test (Advanced)

### Step 1: Start the server
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```

### Step 2: In a NEW terminal, run inference
```bash
set ENV_BASE_URL=http://127.0.0.1:8000
set API_BASE_URL=https://api.openai.com/v1
set API_KEY=test-key-12345
set MODEL_NAME=gpt-4
python inference.py
```

### Step 3: Check the output
You should see:
- 3 lines starting with `[START]`
- 3 lines starting with `[STEP]`
- 3 lines starting with `[END]`
- Exit code: 0 (check with `echo %ERRORLEVEL%`)

## What the judges test

The hackathon validation runs similar steps but with their LLM proxy. Your code must:
- ✓ Wait patiently for server to start (up to 120 seconds)
- ✓ Use their `API_BASE_URL` and `API_KEY` from environment
- ✓ Print structured logs to stdout
- ✓ Exit with code 0 (success)
- ✓ Make at least one API call through their proxy

## Common Issues

**"Server not available"** → Increase wait time in inference.py
**"No structured output"** → Check your print() statements have flush=True
**"No API calls made"** → Verify you're using os.environ["API_BASE_URL"]

## Changes Made (Submission #8)

**Problem:** Server took too long to start (>30s), script crashed
**Fix:** 
- Increased wait from 30s to 120s (60 attempts × 2s)
- Added retry logic if first wait fails
- Added retry for /tasks endpoint (3 attempts with 5s delay)

The judges' environment is slower than local, so patience is key!
