#!/bin/bash
set -e

echo "Starting LegalPro backend..."
echo "PYTHONPATH: $PYTHONPATH"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Listening on: 0.0.0.0:3000"

python -m uvicorn backend.app.main:app \
  --host 0.0.0.0 \
  --port 3000 \
  --log-level info
