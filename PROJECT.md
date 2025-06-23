# PROJECT.md

## Arkitekturöversikt

**Kärnsyfte:**
Applikationen är designad för att användare ska kunna ladda upp filer, vilka sedan verifieras med checksum och virusscanning innan de godkänns för lagring eller nedladdning.

FILES är en skalbar, modulär och portabel webbapplikation som kan köras var som helst med Docker och Docker Compose som enda förutsättning. Den är byggd med moderna teknologier och containerbaserad distribution.

### 1. Frontend

* **Teknik:** Next.js (React)
* **Container:** Docker
* **Funktioner:**

  * Chunked/resumable upload (>10 GB) via tus.io med progressindikator och parallella uppladdningar
  * Administrationspanel (sparar inställningar i PostgreSQL):

    * **All konfiguration och alla inställningar i applikationen hanteras uteslutande i Admin UI; inga ytterligare inställningar finns någon annanstans.**
    * Placering av RBAC-toggle i Admin UI (default OFF) för att växla RBAC on/off
    * **Modes:**

      * **OFF (Configuration Mode):**

        * Applikationen är i utvecklings-/konfigurationsläge
        * Alla endpoints inklusive Admin UI är öppna utan autentisering
        * Tydlig visuell indikation i UI: en banner eller färgad bakgrund med texten “Configuration Mode”
      * **ON (Production Mode):**

        * RBAC och OIDC/AD är aktiverade
        * När RBAC är ON ska admin kunna konfigurera:

          * AD Domain: ange domän eller OIDC-provider URL
          * Admin-grupp: AD-grupp med full tillgång till alla admin-sidor
          * User-grupp: AD-grupp med åtkomst endast till upload- och download-funktioner
    * Toggle för OIDC/AD-integration (default OFF) samt koppla till specifik AD-domain och grupper
    * Toggle för att slå av/på utchecknings- och incheckningsflöden
    * Certifikathantering för HTTPS (uppladdning/rotation)
    * RabbitMQ-inställningar
    * Databasinställningar (pooling, timeouts)
    * Webhooks & notifieringar
    * Retentionsschema & rensningsschema för gamla filer (toggle default OFF)
    * Logotyp-upload (brand logo)
* Övriga funktionstoggles utan omstart

## Nuvarande Status

* **Backend** (FastAPI): Upload, Download, List-API, DB, RabbitMQ ✔️
* **RBAC & Middleware**: Middleware och endpoint guards för RBAC implementerade ✔️
* **Worker**: ClamAV INSTREAM, statusuppdatering ✔️
* **Infra**: Postgres, RabbitMQ, ClamAV, Compose ✔️
* **CI/CD**: Dockerfiles & Compose uppdaterade ✔️
* **Konfiguration**: `.env.example` ✔️

## Återstående Uppgifter

* [ ] Implementera token-verifiering (JWT)
* [ ] Admin-UI (React) för toggles & inställningar
* [ ] Retention/cleanup-task i worker
* [ ] Logging, monitoring, dashboards
* [ ] Unit- & integrationstester

## Nästa Steg

1. 🎯 Implementera token-verifiering (JWT) och extract\_user i middleware
2. Scaffold Admin UI och koppla till backend
3. Schemalägg retention-jobb
4. Skriv tester och setup CI-pipeline
5. Sätt upp GitHub Actions för kontinuerlig integration och enhetstester
6. Skapa dokumentation för driftsättning och konfigurationsguide (README + env)
7. Designa och implementera load- och stresstester för upload- och download-flödet
8. Genomför säkerhetsgranskning och penetrationstest (fokus filvalidering & auth)
9. Förbered och publicera första release-tag (v0.1.0) och skriv changelog

   * Övriga funktionstoggles utan omstart

* Avancerad sök- & filterfunktionalitet (datum, status, filtyp)
* SSO via OIDC/Active Directory för RBAC när ON

### 2. Backend

* **Teknik:** Python + FastAPI
* **Container:** Docker
* **Funktioner:**

  * `POST /upload`: tar emot filer, verifierar checksum, sparar metadata (pending\_scan) i DB och enquear jobb i RabbitMQ
  * `GET /download/{file_id}`: serverar endast `approved` filer
  * Worker-konsumenter plockar jobb och skannar via:

    * ClamAV (obligatorisk, INSTREAM-protokoll)
    * Alternativ motor (VirusTotal API, ClamAV multi-engine), togglebar ON/OFF
  * Filvalidering (MIME-typ + magic bytes)
  * Rate limiting & kvothantering per IP/roll
  * Health-check-endpoints per komponent
  * Circuit breakers & timeouts med degradering vid fel

### 3. Objektlagring

* **Teknik:** Lokala volymer/nätverksfilsystem
* **Funktion:**

  * Sortering i `quarantine` vs `approved` mappar
  * **Retention & Rensning:**

    * Schema definierat i adminpanel (dagligen/veckovis/månadsvis)
    * Toggle för aktivering (default OFF)
    * Schema & toggle sparas i DB för realtidshantering

### 4. Observability & Resilience

* **Metrics & Alerting:** Prometheus-metrics, Grafana/Alertmanager-larm
* **Distributed Tracing:** OpenTelemetry över hela kedjan
* **Circuit Breakers & Timeouts** för resiliency

### 4a. Riskhantering

* **Lagrings-SPOF:** Synkronisering till sekundära volymer, automatiserade återställningsskript
* **RabbitMQ-overhead:** Health-check, automatisk restart via Compose policies
* **Virusscanning-fallback:** Pending-scan med notifiering till admin, begränsa nedladdningar
* **UI-konfig centralisering:** Enhetstester & rollback-flaggor

### 5. Infrastruktur

* **IaC:** Terraform/Pulumi för kluster, nätverk, DNS, certifikat
* **Deploy-strategi:** Blue-Green eller Canary

### 6. Notifieringar & Webhooks

* Webhooks/mail när scanning klar eller karantän
* Konfigurerbart i adminpanelen

### 7. Autentisering & Åtkomstkontroll

* **Administrationspanel (sparar inställningar i PostgreSQL):**

  * Placering av RBAC-toggle i Admin UI (default OFF) för att växla RBAC on/off
  * **Modes:**

    * **OFF (Configuration Mode):**

      * Applikationen är i utvecklings-/konfigurationsläge
      * Alla endpoints inklusive Admin UI är öppna utan autentisering
      * Tydlig visuell indikation i UI: en banner eller färgad bakgrund med texten “Configuration Mode”
    * **ON (Production Mode):**

      * RBAC och OIDC/AD är aktiverade
      * När RBAC är ON ska admin kunna konfigurera:

        * AD Domain: ange domän eller OIDC-provider URL
        * Admin-grupp: AD-grupp med full tillgång till alla admin-sidor
        * User-grupp: AD-grupp med åtkomst endast till upload- och download-funktioner
  * Toggle för OIDC/AD-integration (default OFF) samt koppla till specifik AD-domain och grupper
  * Toggle för att slå av/på utchecknings- och incheckningsflöden
  * Certifikathantering för HTTPS (uppladdning/rotation)
  * RabbitMQ-inställningar
  * Databasinställningar (pooling, timeouts)
  * Webhooks & notifieringar
  * Retentionsschema & rensningsschema för gamla filer (toggle default OFF)
  * Logotyp-upload (brand logo)
  * Övriga funktionstoggles utan omstart
