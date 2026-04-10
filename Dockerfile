FROM --platform=linux/amd64 python:3.9-slim

WORKDIR /app

RUN apt-get update --fix-missing && apt-get install -y postgresql-client && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY . .

RUN chmod +x /app/railway-start.sh

RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p data

ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV PORT=3000

EXPOSE 3000

CMD ["/app/railway-start.sh"]
