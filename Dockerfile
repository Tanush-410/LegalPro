FROM python:3.10

# Railway rebuild trigger - force fresh build

WORKDIR /app

# Copy requirements first
COPY requirements.txt .

# Install dependencies
RUN pip install -r requirements.txt

# Copy everything else
COPY . .

# Ensure data directory exists
RUN mkdir -p /app/data

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
