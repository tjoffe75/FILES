# PROJECT.md

## Arkitekturöversikt

**Kärnsyfte:**
Applikationen är designad för att användare ska kunna ladda upp filer, vilka sedan verifieras med checksum och virusscanning innan de godkänns för lagring eller nedladdning.

FILES är en skalbar, modulär och portabel webbapplikation som kan köras var som helst med Docker och Docker Compose som enda förutsättning. Den är byggd med moderna teknologier och containerbaserad distribution.

### 1. Frontend
- **Teknik:** Next.js (React)
- **Container:** Docker
- **Funktioner:**
  - Chunked/resumable upload (>10 GB) via tus.io med progressindikator och parallella uppladdningar
  - Administrationspanel (sparar inställningar i PostgreSQL):
    - Toggle för RBAC (default OFF)
    - Toggle för OIDC/AD-integration (default OFF) samt AD-grupper (admin/user)
    - Certifikathantering för HTTPS (uppladdning/rotation)
    - RabbitMQ-inställningar
    - Databasinställningar (pooling, timeouts)
    - Webhooks & notifieringar
    - Retentionsschema & rensningsschema för gamla filer (toggle default OFF)
    - Logotyp-upload (brand logo)
    - Övriga funktionstoggles utan omstart
  - Avancerad sök- & filterfunktionalitet (datum, status, filtyp)
  - SSO via OIDC/Active Directory för RBAC när ON

### 2. Backend
- **Teknik:** Python + FastAPI
- **Container:** Docker
- **Funktioner:**
  - `POST /upload`: tar emot filer, verifierar checksum, sparar metadata (pending_scan) i DB och enquear jobb i RabbitMQ
  - `GET /download/{file_id}`: serverar endast `approved` filer
  - Worker-konsumenter plockar jobb och skannar via:
    - ClamAV (obligatorisk, INSTREAM-protokoll)
    - Alternativ motor (VirusTotal API, ClamAV multi-engine), togglebar ON/OFF
  - Filvalidering (MIME-typ + magic bytes)
  - Rate limiting & kvothantering per IP/roll
  - Health-check-endpoints per komponent
  - Circuit breakers & timeouts med degradering vid fel

### 3. Objektlagring
- **Teknik:** Lokala volymer/nätverksfilsystem
- **Funktion:**
  - Sortering i `quarantine` vs `approved` mappar
  - **Retention & Rensning:**
    - Schema definierat i adminpanel (dagligen/veckovis/månadsvis)
    - Toggle för aktivering (default OFF)
    - Schema & toggle sparas i DB för realtidshantering

### 4. Observability & Resilience
- **Metrics & Alerting:** Prometheus-metrics, Grafana/Alertmanager-larm
- **Distributed Tracing:** OpenTelemetry över hela kedjan
- **Circuit Breakers & Timeouts** för resiliency

### 4a. Riskhantering
- **Lagrings-SPOF:** Synkronisering till sekundära volymer, automatiserade återställningsskript
- **RabbitMQ-overhead:** Health-check, automatisk restart via Compose policies
- **Virusscanning-fallback:** Pending-scan med notifiering till admin, begränsa nedladdningar
- **UI-konfig centralisering:** Enhetstester & rollback-flaggor

### 5. Infrastruktur
- **IaC:** Terraform/Pulumi för kluster, nätverk, DNS, certifikat
- **Deploy-strategi:** Blue-Green eller Canary

### 6. Notifieringar & Webhooks
- Webhooks/mail när scanning klar eller karantän
- Konfigurerbart i adminpanelen

### 7. Autentisering & Åtkomstkontroll
- **RBAC i adminpanel:**
  - Toggle RBAC & OIDC/AD
  - Modes:
    - **OFF (Configuration Mode):** alla kontroller OFF, tydlig UI-indikering
    - **ON (Production Mode):** SSO & RBAC aktiverade

---

## Nuvarande Status

- **Backend** (FastAPI): Upload, Download, DB, RabbitMQ ✔️
- **Worker**: ClamAV INSTREAM, statusuppdatering ✔️
- **Infra**: Postgres, RabbitMQ, ClamAV, Compose ✔️
- **CI/CD**: Dockerfiles & Compose uppdaterade ✔️
- **Konfiguration**: `.env.example` ✔️

## Återstående Uppgifter

- [ ] List-API (`GET /files`) med pagination
- [ ] RBAC-middleware & OIDC/AD-integration
- [ ] Admin-UI (React) för toggles & inställningar
- [ ] Retention/cleanup-task i worker
- [ ] Logging, monitoring, dashboards
- [ ] Unit- & integrationstester

## Nästa Steg

1. Implementera List-API i backend
2. Lägg till RBAC & OIDC/AD (Configuration vs Production)
3. Scaffold Admin UI och koppla till backend
4. Schemalägg retention-jobb
5. Skriv tester och setup CI-pipeline
6. Sätt upp GitHub Actions för kontinuerlig integration och enhetstester
7. Skapa dokumentation för driftsättning och konfigurationsguide (README + env)
8. Designa och implementera load- och stresstester för upload- och download-flödet
9. Genomför säkerhetsgranskning och penetrationstest (fokus filvalidering & auth)
10. Förbered och publicera första release-tag (v0.1.0) och skriv changelog
11.