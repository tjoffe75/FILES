# Systemarkitektur

Denna fil beskriver FILES-projektets arkitektur, komponenter, ansvarsområden och informationsflöden för en webbaserad lösning som tillåter användare att:

* Ladda upp filer för virusanalys.
* Utföra checksum-kontroll.
* Visa detaljerade resultat för scanning och checksums.

Systemet är designat för hög skalbarhet och kan integreras med extern autentisering (AD SSO) som stöd.

---

## 1. Komponentöversikt

1. **User-del (Web UI)**

   * Modern och intuitiv webbapplikation.
   * Uppladdning av filer.
   * Visa virusscanningens status och resultat.
   * Visa checksumvärde (t.ex. MD5, SHA256).
2. **Admin-del (Web Admin UI)**

   * Panel för att konfigurera skanningsmotorer och checksum-algoritmer.
   * Hantering av användarbehörigheter och RBAC.
   * Övervakning av systemhälsa och statistik.
3. **Backend API (FastAPI)**

   * Tar emot filuppladdningar.
   * Initierar virusscanning och checksum-beräkning.
   * Exponerar endpoints för resultaten.
4. **Autentisering**

   * JWT-baserad autentisering som primär metod.
   * AD SSO (valfritt) för RBAC och Single Sign-On.
5. **Meddelandekö (RabbitMQ)**

   * Asynkron orkestrering av skannings- och checksum-jobb.
   * Skalbar via klustring.
6. **Worker-tjänster**

   * **Virusworker**: Konsumerar virus-scan-jobb, strömmar fil till ClamAV.
   * **Checksum-worker**: Konsumerar checksum-jobb, beräknar angivna algoritmer.
   * **Optional: Sekventiell sekundär viruseskanning** för verifiering.
7. **Databas (PostgreSQL)**

   * Lagrar metadata, skannings- och checksum-resultat.
   * Designad för replikering og skalbarhet.

---

## 2. Informationsflöde

```text
User Browser  →  Backend API  →  RabbitMQ
            ↖︎               ↙︎
         Web UI          Workers
```

1. **Uppladdning**: Web UI skickar fil till `POST /scan` på Backend.
2. **Jobbskapande**: Backend publicerar två meddelanden i RabbitMQ: ett för virus-scan och ett för checksum.
3. **Virusscanning**: Virusworker hämtar jobb, strömmar fil till ClamAV, uppdaterar resultat i DB.
4. **Checksum**: Checksum-worker hämtar jobb, beräknar MD5/SHA256, sparar värde i DB.
5. **Resultat**: Web UI hämtar status och detaljer via `GET /scan/{id}`.

---

## 3. API-kontrakt

* **`POST /scan`**

  ```json
  Request (multipart/form-data): file, algorithms=["MD5","SHA256"]
  Response:
  {
    "scan_id": "<uuid>",
    "status": "pending"
  }
  ```

* **`GET /scan/{scan_id}`**

  ```json
  {
    "scan_id": "<uuid>",
    "status": "completed",
    "virus_result": "clean",
    "checksum_results": {
      "MD5": "...",
      "SHA256": "..."
    }
  }
  ```

---

## 4. Infrastruktur & Docker Compose

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DB_HOST=postgres
      - RABBITMQ_URL=amqp://rabbitmq
    restart: unless-stopped
  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "15672:15672"
  virusworker:
    build: ./workers/virus
    depends_on: [rabbitmq]
  checksumworker:
    build: ./workers/checksum
    depends_on: [rabbitmq]
  postgres:
    image: postgres:14
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
```

---

## 5. Skalbarhet

* **Backend**: Horisontell skalning bakom lastbalanserare.
* **RabbitMQ**: Kluster för hög tillgänglighet.
* **Workers**: Kör flera instanser av virus- och checksum-workers.
* **DB**: Replikering och sharding stödjs för stora datamängder.

---

## 6. Vidare utveckling

* Integrera Prometheus och Grafana för metrics.
* Stöd för fler checksum-algoritmer.
* Tillägg av fler antivirusmotorer.
