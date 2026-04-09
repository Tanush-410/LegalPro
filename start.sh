#!/bin/bash
set -e

# Debug
echo "Current directory: $(pwd)"
echo "Python path: $(which python3)"
echo "Backend directory exists: [ -d ./backend ] && echo yes || echo no"

# Export PYTHONPATH
export PYTHONPATH=/app:$PYTHONPATH

# Start the application
exec python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
