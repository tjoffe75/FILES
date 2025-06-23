# PROJECT.md

## Arkitekturöversikt

**Kärnsyfte:**
Applikationen är designad för att användare ska kunna ladda upp filer, vilka sedan verifieras med checksum och virusscanning innan de godkänns för lagring eller nedladdning.

**Användarupplevelse:**

* 🎨 Gränssnittet ska vara tydligt, intuitivt och enkelt att använda genom hela applikationen, både i Admin UI och i Upload/Download-flöden.

**Uppföljning av kärnsyfte:**

* ✅ Upload API sparar metadata och checksum vid mottagning
* ✅ Asynkron virusscanning (ClamAV INSTREAM) säkerställer ren fil
* ✅ Download API levererar endast `approved` filer
* ✅ RBAC och toggles skyddar åtkomst när produktion
* ✅ Admin UI hanterar alla konfigurationsbehov

### 1. Frontend

* **Teknik:** Vite + React
* **Container:** Docker
* **Funktioner:**

  * `POST /upload`: tar emot filer, verifierar checksum, sparar metadata (pending\_scan) och enquear jobb i RabbitMQ
  * `GET /files` & `GET /download/{file_id}`:

    * När RBAC är **OFF**: alla kan lista och ladda ned godkända filer
    * När RBAC är **ON**: `GET /files` returnerar endast filer där `owner_id = user.sub`; admin-roller ser **alla** filer
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

### 4. Logging & Logghantering

* **Loggning:**

  * Skriva applikationsloggar till fil (roterande filer med daglig rullning)
  * Konfigurerbar loggnivå (DEBUG/INFO/WARN/ERROR) via Admin UI
* **Loggläsare i Admin UI:**

  * Ny vy i Admin UI för att visa senaste loggradder
  * Filter och sök i loggar (datum, nivå, meddelande)
  * Möjlighet att ladda ner loggfil

### 5. Observability & Resilience. Observability & Resilience

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

* [ ] Formulärvalidering och felhantering i SettingsPage och UploadPage (loading/spinner, error states)
* [ ] Logotyp-uppladdning: ny `POST /admin/logo` endpoint och UI-komponent
* [ ] Retention cleanup-jobb i worker + toggle i UI
* [ ] **Sekundär virusmotor**: integrera valfri alternativa scanningstjänst (VirusTotal API eller ClamAV multi-engine) som optional toggle
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

1. 🖼️ **Logotyp-uppladdning**

   * Backend: `POST /admin/logo`, spara URL i `settings.logo_url`
   * Frontend: fil-input + preview i SettingsPage

2. 🗑️ **Retention Cleanup**

   * Worker: schemalägg rensning enligt `settings.cleanup_schedule`
   * Frontend: toggle för `retention_enabled`
     
3. 🧪 **Testautomation & CI**

   * Skriv och kör enhetstester (pytest, Jest)
   * Sätt upp GitHub Actions: bygg, lint, test för backend & frontend

4. 📊 **Observability**

   * Lägg till `/metrics` i FastAPI m.h.a. Prometheus-instrumentering
   * Integrera OpenTelemetry i API och worker

5. 🛡 **Input‑validering & Säkerhet**

   * Validera MIME-typ + magic bytes i upload
   * Begränsa maximal filstorlek

6. ⚙️ **Cache & Async**

   * Cachea settings med `lru_cache` eller batch-hämtning
   * Överväg `asyncpg` + `aio-pika` för asynkrona anrop

8. 🎯 **Release v0.1.0**

   * Paketera Admin UI image, uppdatera Compose
   * Tagga och publicera med changelog


