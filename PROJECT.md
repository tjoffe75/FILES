# PROJECT.md

## Arkitekturöversikt

**Kärnsyfte:**
Applikationen är designad för att användare ska kunna ladda upp filer, vilka sedan verifieras med checksum och virusscanning innan de godkänns för lagring eller nedladdning.

FILES är en skalbar, modulär och portabel webbapplikation som kan köras var som helst med Docker och Docker Compose som enda förutsättning. Den är byggd med moderna teknologier och containerbaserad distribution.

### 1. Frontend

* **Teknik:** Vite + React
* **Container:** Docker
* **Funktioner:**

  * Enkel och intuitiv användarupplevelse med tydliga kontroller och minimal komplexitet
  * **Klar och användarvänlig UI även för uppladdnings- och nedladdningssidor**
  * Chunked/resumable upload (>10 GB) via tus.io med progressindikator och parallella uppladdningar
  * Administrationspanel (sparar inställningar i PostgreSQL):

    * **All konfiguration hanteras uteslutande i Admin UI**
    * RBAC-toggle (default OFF) för att växla mellan **Configuration Mode** och **Production Mode**
    * OIDC/AD-toggle (default OFF) med fält för AD-domain, admin- och user-grupper
    * Certifikathantering för HTTPS
    * RabbitMQ-, DB- och webhook-/notifierings-inställningar
    * Retentionsschema & rensningsschema (toggle default OFF)
    * Logotyp-upload (brand logo)
  * Avancerad sök- och filterfunktionalitet (datum, status, filtyp)

### 2. Backend

* **Teknik:** Python + FastAPI
* **Container:** Docker
* **Funktioner:**

  * `POST /upload`: tar emot filer, verifierar checksum, sparar metadata (pending\_scan) och enquear jobb i RabbitMQ
  * `GET /files` & `GET /download/{file_id}`: listar och serverar endast `approved` filer
  * `GET` & `POST /admin/settings`: läs och spara alla Admin-inställningar i `settings`-tabell
  * RBAC/SSO-middleware med JWT-verifiering och rollkontroll
  * Worker-konsumenter med ClamAV INSTREAM och valfri sekundär motor (togglebar)
  * Filvalidering (MIME-typ + magic bytes), rate limiting och health checks

### 3. Objektlagring

* **Teknik:** Lokala volymer eller nätverksfilsystem
* **Funktion:**

  * Sortering i `quarantine` vs `approved` mappar
  * **Retention & rensning:**

    * Schema definierat i Admin UI (daily/weekly/monthly)
    * Toggle för aktivering (default OFF), sparas i DB

### 4. Observability & Resilience

* Prometheus-metrics och Grafana-alerts
* OpenTelemetry-distributed tracing
* Circuit breakers & timeouts

### 5. Riskhantering

* Synkronisering av filer till sekundär volym (SPOF)
* RabbitMQ health checks och auto-restart
* Pending-scan-fallback och notifiering

### 6. Infrastruktur

* IaC med Terraform/Pulumi
* Blue-Green/Canary deployment

### 7. Notifieringar & Webhooks

* Skicka webhooks/mail vid scanning och karantän

---

## Nuvarande Status

* **Backend** (FastAPI): Upload, List, Download, Admin Settings API ✔️
* **RBAC & JWT**: Middleware och token-verifiering implementerat ✔️
* **Worker**: ClamAV INSTREAM, statusuppdatering ✔️
* **Infra**: Postgres, RabbitMQ, ClamAV, Compose ✔️
* **Admin UI scaffold**: Vite + React initierat, routing ✔️
* **SettingsPage & UploadPage**: Implementerade och testade ✔️

## Återstående Uppgifter

* [ ] Banner för "Configuration Mode" i Admin UI när `rbac_enabled == false`
* [ ] Formulärvalidering och felhantering i SettingsPage och UploadPage (loading/spinner, error states)
* [ ] Logotyp-uppladdning: ny `POST /admin/logo` endpoint och UI-komponent
* [ ] Retention cleanup-jobb i worker + toggle i UI
* [ ] Enhetstester: backend (pytest) och frontend (Jest + React Testing Library)
* [ ] Docker-image för Admin UI och uppdatera `docker-compose.yaml`
* [ ] GitHub Actions: bygg, lint, test för backend och frontend
* [ ] End-to-end-testflöden (upload → scan → toggle → download)
* [ ] Slutgiltig dokumentation: `README.md`, API-spec, konfigurationsguide
* [ ] Instrumentera observability:

  * Lägg till Prometheus-metrics i FastAPI (`/metrics` endpoint)
  * OpenTelemetry-distributed tracing för API och worker
* [ ] Input-validering i backend:

  * Kolla `file.content_type` och magic bytes vid upload
  * Begränsa maximal filstorlek och skydd mot zip-bombs
* [ ] Settings-cache:

  * Lägg in-memory cache (t.ex. `lru_cache`) för settings-lookup eller batch-slå upp flera nycklar
* [ ] Asynkrona förbättringar:

  * Överväg `asyncpg` och `aio-pika` för DB- och RabbitMQ-anrop för bättre skalbarhet

## Nästa Steg

1. 🔔 **Konfigurationsbanner**

   * Implementera i `SettingsPage.jsx` baserat på `settings.rbac_enabled` (red banner)
2. 🖼️ **Logotyp-uppladdning**

   * Backend: `POST /admin/logo`, spara fil och uppdatera `settings.logo_url`
   * Frontend: fil-input, förhandsvisning och upload via axios
3. 🗑️ **Retention Cleanup**

   * Worker: schemalägg rensning enligt `settings.cleanup_schedule`
   * Frontend: toggle för `retention_enabled`
4. 📊 **Observability**

   * Lägg till `/metrics` i FastAPI med Prometheus-instrumentering
   * Integrera OpenTelemetry tracing i både API och worker
5. 🛡 **Input-validering & Säkerhet**

   * Validera MIME-typ och magic bytes i upload-endpoint
   * Ange maximal filstorlek
6. 🏎 **Async Uppsättning**

   * Migrera till `asyncpg` och `aio-pika` för icke-blockerande IO
   * Minska latens vid samtidiga anrop
7. 🧪 **Testautomation & CI**

   * Skriv och kör enhetstester, starta GitHub Actions-workflow
   * Inkludera integrationstest för upload-scan-download
8. 📦 **Docker & Release**

   * Paketera Admin UI image, uppdatera Compose
   * Tagga och publicera v0.1.0 med changelog


