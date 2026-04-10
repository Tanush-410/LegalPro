FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy both root and backend requirements
COPY requirements.txt .
COPY backend/requirements.txt ./backend-requirements.txt

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt && \
    ([ -f backend-requirements.txt ] && pip install --no-cache-dir -r backend-requirements.txt || true)

# Copy entire application code
COPY . /app

# Set Python path explicitly
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Run application
CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
