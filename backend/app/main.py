# backend/app/main.py

import os
import uuid
import hashlib
import pika
import psycopg2

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict

app = FastAPI()

# ─── Hjälpfunktioner (måste ligga före middleware) ─────────────────────────────
def get_db_conn():
    return psycopg2.connect(os.getenv("DATABASE_URL"))

def get_setting(key: str) -> bool:
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT value FROM settings WHERE key = %s", (key,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    return bool(row and row[0].lower() == "true")
# ────────────────────────────────────────────────────────────────────────────────

# ─── RBAC/SSO‐middleware ────────────────────────────────────────────────────────
@app.middleware("http")
async def rbac_middleware(request: Request, call_next):
    # Om RBAC är OFF, låt allt passera
    if not get_setting("rbac_enabled"):
        return await call_next(request)

    # Annars krävs en Authorization-header
    token = request.headers.get("Authorization")
    if not token:
        return JSONResponse({"detail": "Unauthorized"}, status_code=401)

    # TODO: verifiera token och sätt request.state.user
    # user = verify_jwt(token)
    # request.state.user = user

    return await call_next(request)
# ────────────────────────────────────────────────────────────────────────────────

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/upload")
async def upload(request: Request, file: UploadFile = File(...), owner_id: str = "anonymous"):
    # RBAC‐skydd
    if get_setting("rbac_enabled"):
        user = getattr(request.state, "user", None)
        if not user or ("user" not in user.roles and "admin" not in user.roles):
            raise HTTPException(status_code=403, detail="Forbidden")

    # 1) Ensure upload dir
    uploads_dir = os.path.join(os.getcwd(), "app", "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    # 2) Spara och checksum
    file_id = str(uuid.uuid4())
    save_path = os.path.join(uploads_dir, f"{file_id}_{file.filename}")
    sha256 = hashlib.sha256()
    with open(save_path, "wb") as out_file:
        while chunk := await file.read(1024 * 1024):
            sha256.update(chunk)
            out_file.write(chunk)
    checksum = sha256.hexdigest()

    # 3) Skriv metadata
    try:
        conn = get_db_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO files (id, filename, checksum, status, owner_id) VALUES (%s, %s, %s, %s, %s)",
            (file_id, file.filename, checksum, "pending_scan", owner_id),
        )
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DB error: {e}")

    # 4) Publicera jobb
    try:
        params = pika.URLParameters(os.getenv("RABBITMQ_URL"))
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue="upload_jobs", durable=True)
        channel.basic_publish(
            exchange="",
            routing_key="upload_jobs",
            body=file_id.encode(),
            properties=pika.BasicProperties(delivery_mode=2),
        )
        connection.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Message queue error: {e}")

    # 5) Returnera svar
    return {"file_id": file_id, "checksum": checksum}


@app.get("/files", response_model=List[Dict])
async def list_files(request: Request, owner_id: str = "anonymous"):
    # RBAC‐skydd
    if get_setting("rbac_enabled"):
        user = getattr(request.state, "user", None)
        if not user or ("user" not in user.roles and "admin" not in user.roles):
            raise HTTPException(status_code=403, detail="Forbidden")

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, filename, status, created_at FROM files WHERE owner_id = %s ORDER BY created_at DESC",
        (owner_id,),
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()

    return [
        {"id": str(r[0]), "filename": r[1], "status": r[2], "created_at": r[3].isoformat()}
        for r in rows
    ]


@app.get("/download/{file_id}")
async def download(request: Request, file_id: str, owner_id: str = "anonymous"):
    # RBAC‐skydd
    if get_setting("rbac_enabled"):
        user = getattr(request.state, "user", None)
        if not user or ("user" not in user.roles and "admin" not in user.roles):
            raise HTTPException(status_code=403, detail="Forbidden")

    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT filename, status, owner_id FROM files WHERE id = %s", (file_id,))
    row = cur.fetchone()
    cur.close()
    conn.close()

    if not row:
        raise HTTPException(status_code=404, detail="File not found")

    filename, status, db_owner = row
    if status != "approved":
        raise HTTPException(status_code=403, detail="File not approved for download")

    file_path = os.path.join(os.getcwd(), "app", "uploads", f"{file_id}_{filename}")
    return FileResponse(path=file_path, filename=filename, media_type="application/octet-stream")
