FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

RUN apt-get update --fix-missing && apt-get install -y postgresql-client && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /tmp/
RUN python -m pip install --no-cache-dir -r /tmp/requirements.txt

COPY . .
RUN mkdir -p data

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=8000

EXPOSE 8000

CMD python -m uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000}
