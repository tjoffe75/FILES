# backend/app/main.py

import os
import uuid
import hashlib
import pika
import psycopg2
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

def get_db_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...), owner_id: str = "anonymous"):
    # 1) Ensure upload directory exists
    uploads_dir = os.path.join(os.getcwd(), "app", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    # 2) Save file chunk by chunk and compute SHA256
    file_id = str(uuid.uuid4())
    save_path = os.path.join(uploads_dir, f"{file_id}_{file.filename}")
    sha256 = hashlib.sha256()
    with open(save_path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            sha256.update(chunk)
            out_file.write(chunk)
    checksum = sha256.hexdigest()

    # 3) Insert metadata into Postgres
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO files (id, filename, checksum, status, owner_id) VALUES (%s, %s, %s, %s, %s)",
            (file_id, file.filename, checksum, "pending_scan", owner_id)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    # 4) Publish job to RabbitMQ
    try:
        params = pika.URLParameters(os.getenv("RABBITMQ_URL"))
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue="upload_jobs", durable=True)
        channel.basic_publish(
            exchange="",
            routing_key="upload_jobs",
            body=file_id,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message queue error: {e}")

    # 5) Return the generated ID and checksum
    return {"file_id": file_id, "checksum": checksum}

from typing import List, Dict

@app.get("/files", response_model=List[Dict])
async def list_files(owner_id: str = "anonymous"):
    """
    Returnerar en lista på alla filer för angivet owner_id,
    med fält: id, filename, status och created_at.
    """
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, filename, status, created_at FROM files WHERE owner_id = %s ORDER BY created_at DESC",
        (owner_id,)
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    result = []
    for file_id, filename, status, created_at in rows:
        result.append({
            "id": str(file_id),
            "filename": filename,
            "status": status,
            "created_at": created_at.isoformat()
        })
    return result

@app.get("/download/{file_id}")
async def download(file_id: str, owner_id: str = "anonymous"):
    # Retrieve metadata
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT filename, status, owner_id FROM files WHERE id = %s",
        (file_id,)
    )
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    filename, status, db_owner = row
    # Check approved status
    if status != "approved":
        raise HTTPException(status_code=403, detail="File not approved for download")

    # Serve file
    file_path = os.path.join(os.getcwd(), "app", "uploads", f"{file_id}_{filename}")
    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")
