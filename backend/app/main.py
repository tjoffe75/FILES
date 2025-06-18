# backend/app/main.py

import os
import uuid
import hashlib

from fastapi import FastAPI, UploadFile, File, HTTPException
import psycopg2

app = FastAPI()

def get_db_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/upload")
async def upload(file: UploadFile = File(...), owner_id: str = "anonymous"):
    # 1) Se till att upload-mappen finns
    uploads_dir = "./app/uploads"
    os.makedirs(uploads_dir, exist_ok=True)

    # 2) Spara fil chunk för chunk och bygg SHA256-checksum
    file_id = str(uuid.uuid4())
    save_path = f"{uploads_dir}/{file_id}_{file.filename}"
    sha256 = hashlib.sha256()
    with open(save_path, "wb") as out:
        while True:
            chunk = await file.read(1024*1024)
            if not chunk:
                break
            sha256.update(chunk)
            out.write(chunk)
    checksum = sha256.hexdigest()

    # 3) Skriv metadata till Postgres
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO files (id, filename, checksum, status, owner_id) VALUES (%s,%s,%s,%s,%s)",
            (file_id, file.filename, checksum, "pending_scan", owner_id)
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    # 4) Returnera UUID och checksum
    return {"file_id": file_id, "checksum": checksum}
