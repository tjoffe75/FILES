

Arkitekturöversikt

Kärnsyfte:
Applikationen är designad för att användare ska kunna ladda upp filer, vilka sedan verifieras med checksum och virusscanning innan de godkänns för lagring eller nedladdning.

FILES är en skalbar, modulär och portabel webbapplikation som kan köras var som helst med Docker och Docker Compose som enda förutsättning. Den är byggd med moderna teknologier och containerbaserad distribution.

1. Frontend

Teknik: Vite + React

Container: Docker

Funktioner:

Enkel och intuitiv användarupplevelse med tydliga kontroller och minimal komplexitet

Klar och användarvänlig UI även för uppladdnings- och nedladdningssidor

Chunked/resumable upload (>10 GB) via tus.io med progressindikator och parallella uppladdningar

Administrationspanel (sparar inställningar i PostgreSQL):

All konfiguration hanteras uteslutande i Admin UI

RBAC-toggle (default OFF) för att växla mellan Configuration Mode och Production Mode

OIDC/AD-toggle (default OFF) med fält för AD-domain, admin- och user-grupper

Certifikathantering för HTTPS

RabbitMQ-, DB- och webhook-/notifierings-inställningar

Retentionsschema & rensningsschema (toggle default OFF)

Logotyp-upload (brand logo)

Avancerad sök- och filterfunktionalitet (datum, status, filtyp) (datum, status, filtyp)

2. Backend

Teknik: Python + FastAPI

Container: Docker

Funktioner:

POST /upload: tar emot filer, verifierar checksum, sparar metadata (pending_scan) och enquear jobb i RabbitMQ

GET /files & GET /download/{file_id}: listar och serverar endast approved filer

GET & POST /admin/settings: läs och spara alla Admin-inställningar i settings-tabell

RBAC/SSO-middleware med JWT-verifiering och rollkontroll

Worker-konsumenter med ClamAV INSTREAM och valfri sekundär motor (togglebar)

Filvalidering (MIME-typ + magic bytes), rate limiting och health checks

3. Objektlagring

Teknik: Lokala volymer eller nätverksfilsystem

Funktion:

Sortering i quarantine vs approved mappar

Retention & rensning:

Schema definierat i Admin UI (daily/weekly/monthly)

Toggle för aktivering (default OFF), sparas i DB

4. Observability & Resilience

Prometheus-metrics och Grafana-alerts

OpenTelemetry-distributed tracing

Circuit breakers & timeouts

5. Riskhantering

Synkronisering av filer till sekundär volym (SPOF)

RabbitMQ health checks och auto-restart

Pending-scan-fallback och notifiering

6. Infrastruktur

IaC med Terraform/Pulumi

Blue-Green/Canary deployment

7. Notifieringar & Webhooks

Skicka webhooks/mail vid scanning och karantän

Nuvarande Status

Backend (FastAPI): Upload, List, Download, Admin Settings API ✔️

RBAC & JWT: Middleware och token-verifiering implementerat ✔️

Worker: ClamAV INSTREAM, statusuppdatering ✔️

Infra: Postgres, RabbitMQ, ClamAV, Compose ✔️

Admin UI scaffold: Vite + React initierat, routing ✔️

SettingsPage & UploadPage: Implementerade och testade ✔️

Återstående Uppgifter



Nästa Steg

🔔 Konfigurationsbanner

Implementera i SettingsPage.jsx baserat på settings.rbac_enabled

🖼️ Logotyp-uppladdning

Backend: POST /admin/logo, lagra URL i settings.logo_url

Frontend: fil-input och preview i SettingsPage

🗑️ Retention Cleanup

Worker: schemalägg rensning enligt settings.cleanup_schedule

Frontend: toggle för retention_enabled

🧪 Testning

Skapa och kör enhetstester för alla endpoints och UI-komponenter

📦 Docker & CI

Paketera Admin UI-image, uppdatera Compose, skriv GitHub Actions

🚀 Release v0.1.0

Tagga, changelog och publicera första release