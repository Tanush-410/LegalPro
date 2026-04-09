#!/usr/bin/env python3
"""
Railway entry point - sets up PYTHONPATH correctly
"""
import sys
import os

# Add the current directory to Python path so 'backend' module can be found
sys.path.insert(0, os.getcwd())

# Now import and run uvicorn
import uvicorn
from backend.app.main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
