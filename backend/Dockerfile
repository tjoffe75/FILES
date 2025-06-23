# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Kopiera applikationskod
COPY app/ ./app/

# Installera FastAPI, Uvicorn, PostgreSQL-drivrutin, multipart-stöd och RabbitMQ-klient
RUN pip install fastapi uvicorn psycopg2-binary python-multipart pika

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

RUN pip install fastapi uvicorn psycopg2-binary python-multipart pika
+RUN pip install python-jose[cryptography]
