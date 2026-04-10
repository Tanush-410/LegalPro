#!/bin/bash
set -e

echo "Starting LegalPro backend..."
echo "PYTHONPATH: $PYTHONPATH"
echo "Current directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Listening on: 0.0.0.0:${PORT:-8000}"

python -m uvicorn backend.app.main:app \
  --host 0.0.0.0 \
  --port ${PORT:-8000} \
  --log-level info
