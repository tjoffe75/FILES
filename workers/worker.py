# Skapa filen på nytt
import time
import os
import socket
import psycopg2
import pika

# Miljövariabler för anslutningar
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
DATABASE_URL   = os.getenv("DATABASE_URL")
CLAMAV_HOST    = os.getenv("CLAMAV_HOST", "clamav")
CLAMAV_PORT    = int(os.getenv("CLAMAV_PORT", 3310))

def get_db_conn():
    return psycopg2.connect(DATABASE_URL)

def scan_file(filepath: str) -> str:
    """
    Skickar filen till ClamAV-daemont via INSTREAM och returnerar svarstexten.
    """
    # 1) Vänta på att ClamAV ska vara redo
    attempt = 0
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((CLAMAV_HOST, CLAMAV_PORT))
            break
        except ConnectionRefusedError:
            attempt += 1
            if attempt >= 5:
                raise
            print(f"[*] ClamAV inte redo, försök {attempt}/5 – väntar 3 sek")
            time.sleep(3)

    # 2) Starta INSTREAM med korrekt kommando
    s.send(b"zINSTREAM\x00")

    # 3) Skicka filinnehåll i chunkar
    with open(filepath, "rb") as f:
        chunk = f.read(1024)
        while chunk:
            size = len(chunk).to_bytes(4, byteorder="big")
            s.send(size + chunk)
            chunk = f.read(1024)

    # 4) Avsluta stream
    s.send(b"\x00\x00\x00\x00")

    # 5) Läs ClamAV-svaret
    response = b""
    while True:
        data = s.recv(4096)
        if not data:
            break
        response += data
    s.close()
    return response.decode()

def callback(ch, method, properties, body):
    file_id = body.decode()
    print(f"[worker] Got job: {file_id}")

    # Hämta filnamn från databasen
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT filename FROM files WHERE id = %s", (file_id,))
    row = cur.fetchone()
    if not row:
        print(f"[worker] File ID {file_id} not found in DB, ack and skip")
        ch.basic_ack(delivery_tag=method.delivery_tag)
        conn.close()
        return

    filename = row[0]
    filepath = f"/app/uploads/{file_id}_{filename}"

    # Skanna filen via INSTREAM
    result = scan_file(filepath)
    print(f"[worker] ClamAV response for {file_id}: {result.strip()}")

    # Bestäm status
    if "FOUND" in result:
        status = "quarantine"
    else:
        status = "approved"

    # Uppdatera status i databasen
    cur.execute(
        "UPDATE files SET status = %s WHERE id = %s",
        (status, file_id)
    )
    conn.commit()
    print(f"[worker] Updated status for {file_id} to {status}")
    cur.close()
    conn.close()

    # Ack:a meddelandet
    ch.basic_ack(delivery_tag=method.delivery_tag)

def main():
    # Retry för RabbitMQ
    params = pika.URLParameters(RABBITMQ_URL)
    connection = None
    for attempt in range(1, 11):
        try:
            connection = pika.BlockingConnection(params)
            break
        except pika.exceptions.AMQPConnectionError:
            print(f"[*] RabbitMQ inte redo, försök {attempt}/10 – väntar 5 sek...")
            time.sleep(5)
    if not connection or connection.is_closed:
        print("[!] Kunde inte koppla till RabbitMQ efter 10 försök. Avslutar.")
        return

    channel = connection.channel()
    channel.queue_declare(queue="upload_jobs", durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue="upload_jobs", on_message_callback=callback)

    print("[worker] Connected to RabbitMQ, waiting for jobs...")
    channel.start_consuming()

if __name__ == "__main__":
    main()
EOF
