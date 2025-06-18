# backend/Dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY app/ ./app/

# Installera FastAPI, Uvicorn, PostgreSQL-drivrutin och multipart-stöd
RUN pip install fastapi uvicorn psycopg2-binary python-multipart

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
