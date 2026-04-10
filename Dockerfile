FROM python:3.10

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Copy and install requirements
COPY requirements.txt .
RUN pip install --upgrade pip setuptools && pip install -r requirements.txt

# Copy application
COPY . .

# Create data directory
RUN mkdir -p data

# Set environment
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
