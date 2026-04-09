#!/bin/bash
cd /app
export PYTHONPATH=/app:$PYTHONPATH
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
