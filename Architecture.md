# Systemarkitektur

Denna fil beskriver FILES-projektets arkitektur, komponenter, ansvarsområden och informationsflöden för en webbaserad lösning som tillåter användare att:

* Ladda upp filer för virusscanning.
* Utföra checksum-kontroll (t.ex. MD5, SHA256).
* Visa detaljerade resultat för både virusscanning och checksums.

Systemet är designat för hög skalbarhet, modulär utbyggnad och dynamisk konfiguration via databasen. Extern autentisering (AD SSO) stöds som en valfri RBAC-funktion.

---

## 1. Komponentöversikt

1. **User-del (Web UI)**

   * Modern och intuitiv webbapplikation byggd med React.
   * Uppladdning av filer för skanning.
   * Visa skanningsstatus och resultat.
   * Visa checksumvärden (MD5, SHA256).
2. **Admin-del (Web Admin UI)**

   * Panel för konfiguration av skanningsmotorer och checksum-algoritmer.
   * Hantering av användare och RBAC-regler, drivet av databaslagrade policies.
   * Realtidsövervakning av systemhälsa, loggar och statistik.
3. **Backend API (FastAPI)**

   * **Endpoints**

     * `POST /scan`: Initiera virusscanning och checksum-beräkning; publicerar jobb i RabbitMQ.
     * `GET /scan/{id}`: Hämta skannings- och checksum-resultat.
     * `GET/POST /config`: Läsa och uppdatera konfigurationsinställningar (lagrade i DB).
     * `GET /health`: Kontroll av DB- och RabbitMQ-anslutning.
   * Horisontellt skalbar bakom en lastbalanserare.
4. **Autentisering**

   * JWT-baserad autentisering för alla API-anrop.
   * AD SSO (OpenID Connect) som valfri RBAC-funktion.
5. **Meddelandekö (RabbitMQ)**

   * Asynkron orkestrering av skannings- och checksum-jobb.
   * Schema- och policybaserade queues: `virus_scan`, `checksum_calc`, `secondary_scan`.
   * Kan klustras för hög tillgänglighet.
6. **Worker-tjänster**

   * **Virus-worker**

     * Konsumerar `virus_scan`-jobb.
     * Strömmar fil till ClamAV.
     * Uppdaterar resultat i DB.
     * Publicerar jobb till `secondary_scan` om sekundär skanning aktiverad.
   * **Checksum-worker**

     * Konsumerar `checksum_calc`-jobb.
     * Beräknar angivna checksum-algoritmer.
     * Sparar värden i DB.
   * **Secondary-scan-worker (valfri)**

     * Konsumerar `secondary_scan`.
     * Skickar fil till en sekundär antivirusmotor för verifiering.
7. **Databas (PostgreSQL)**

   * Lagrar metadata för filer, skanningsstatus, checksum-resultat och dynamisk konfiguration.
   * Stöd för replikering och sharding för skalbarhet.
8. **Virus­sökning (ClamAV)**

   * Kan driftsättas i flera instanser bakom load balancer.
9. **Optional: Sekventiell sekundär viruseskanning**

   * Efter primär ClamAV-scanning kan fil skickas till extra antivirusmotor för verifiering.

---

## 2. Informationsflöde

```text
User Browser  →  Backend API  →  RabbitMQ
            ↙︎             ↘︎  ↘︎
    Web UI (scan/status)     Workers → DB
```

1. **Uppladdning**: Web UI anropar `POST /scan` med fil och checksum-algoritmer.
2. **Jobbskapande**: Backend publicerar jobb i `virus_scan` och `checksum_calc` queues.
3. **Virusscanning**: Virus-worker processar jobb, uppdaterar DB, pushar `secondary_scan` om aktiverat.
4. **Checksum**: Checksum-worker processar jobb, beräknar och sparar resultat.
5. **Sekundär skanning**: Secondary-scan-worker verifierar resultat vid behov.
6. **Resultat**: Web UI hämtar via `GET /scan/{id}`.

---

## 3. Databasmodell

```sql
CREATE TABLE scans (
  id UUID PRIMARY KEY,
  filename TEXT NOT NULL,
  content_type TEXT NOT NULL,
  size BIGINT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  status TEXT NOT NULL CHECK (status IN ('pending','scanning','completed','failed')),
  virus_result JSONB,
  checksum_results JSONB,
  config JSONB       -- Dynamiska inställningar per scan
);

CREATE TABLE config (
  key TEXT PRIMARY KEY,
  value JSONB NOT NULL,
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
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
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval: 30s
      timeout: 10s
      retries: 3

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "15672:15672"

  virus-worker:
    build: ./workers/virus
    depends_on: [rabbitmq]
    environment:
      - RABBITMQ_URL=amqp://rabbitmq

  checksum-worker:
    build: ./workers/checksum
    depends_on: [rabbitmq]
    environment:
      - RABBITMQ_URL=amqp://rabbitmq

  secondary-worker:
    build: ./workers/secondary
    depends_on: [rabbitmq]
    environment:
      - RABBITMQ_URL=amqp://rabbitmq

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
* **RabbitMQ**: Klustring för hög tillgänglighet.
* **Workers**: Multipla instanser per typ (virus, checksum, secondary).
* **Databas**: Replikering och sharding.
* **Dynamisk konfiguration**: Uppdateringar i `config`-tabellen reflekteras utan omstart.

---

*Uppdaterad: 2025-06-24*
