#!/bin/bash
# Start the environment server in the background
echo "Starting environment server..."
uvicorn app:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to be ready
echo "Waiting for server to start..."
sleep 5

# Check if server is running
if ! kill -0 $SERVER_PID 2>/dev/null; then
    echo "ERROR: Server failed to start"
    exit 1
fi

echo "Server started successfully (PID: $SERVER_PID)"

# Run the inference script
echo "Running inference script..."
python inference.py
INFERENCE_EXIT_CODE=$?

# Kill the server
echo "Stopping server..."
kill $SERVER_PID 2>/dev/null || true

# Exit with inference script's exit code
exit $INFERENCE_EXIT_CODE
