#!/bin/bash
# Set the working directory - Railway uses /app, local uses current directory
if [ -d "/app" ]; then
  cd /app
else
  cd "$(dirname "$0")"
fi

# Set PYTHONPATH to include current directory
export PYTHONPATH=.:$PYTHONPATH

# Start the application
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
