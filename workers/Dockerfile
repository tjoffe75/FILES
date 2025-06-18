# workers/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Kopiera in koden
COPY . .

# Installera systemberoenden för ClamAV-daemon (INSTREAM)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       clamav \
       clamav-daemon \
    && rm -rf /var/lib/apt/lists/*

# Installera Python-beroenden
RUN pip install pika psycopg2-binary

# Unbuffered output så print() skrivs direkt
CMD ["python", "-u", "worker.py"]
