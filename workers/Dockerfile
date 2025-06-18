# workers/Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install pika  # RabbitMQ-client, plus clamav-lib om du använder
CMD ["python", "worker.py"]
