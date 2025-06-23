# PROJECT.md

## Arkitekturöversikt

**Kärnsyfte:**  
Applikationen är designad för att användare ska kunna ladda upp filer, vilka sedan verifieras med checksum och virusscanning innan de godkänns för lagring eller nedladdning.

**Användarupplevelse:**  
🎨 Gränssnittet ska vara tydligt, intuitivt och enkelt att använda genom hela applikationen, både i Admin UI och i Upload/Download-flöden.

**Uppföljning av kärnsyfte:**  
- ✅ Upload API sparar metadata och checksum vid mottagning  
- ✅ Asynkron virusscanning (ClamAV INSTREAM) säkerställer ren fil  
- ✅ Download API levererar endast `approved` filer  
- ✅ RBAC och toggles skyddar åtkomst när produktion  
- ✅ Admin UI hanterar alla konfigurationsbehov  

### 1. Frontend

* **Teknik:** Vite + React  
* **Container:** Docker  
* **Funktioner:**
  * `POST /upload`: tar emot filer, verifierar checksum, sparar metadata (pending_scan) och enquear jobb i RabbitMQ  
  * `GET /files` & `GET /download/{file_id}`:  
    - **RBAC OFF:** alla kan lista och ladda ned godkända filer  
    - **RBAC ON:** vanliga användare ser bara sina egna filer; admin ser alla  
  * `GET` & `POST /admin/settings`: läs och spara alla Admin-inställningar i `settings`-tabell  
  * RBAC/SSO-middleware med JWT-verifiering och rollkontroll  
  * UI-komponenter för logotyp-upload, retention-toggle, loggläsare, loading/spinner och felmeddelanden  

### 2. Objektlagring

* **Teknik:** Lokala volymer eller nätverksfilsystem  
* **Funktion:**  
  * Sortering i `quarantine` vs `approved` mappar  
  * **Retention & rensning:**  
    - Schema definierat i Admin UI (daily/weekly/monthly)  
    - Toggle för aktivering (default OFF), sparas i DB  

### 3. Logging & Logghantering

* **Loggning:**  
  * Skriva applikationsloggar till fil (roterande dagligen)  
  * Konfigurerbar loggnivå (DEBUG/INFO/WARN/ERROR) via Admin UI  
* **Loggläsare i Admin UI:**  
  * Visa senaste loggradder med filter (datum, nivå, meddelande)  
  * Möjlighet att ladda ner loggfil  

### 4. Observability & Resilience

* Prometheus-metrics och Grafana-alerts  
* OpenTelemetry-distributed tracing  
* Circuit breakers & timeouts  

### 5. Riskhantering

* Synkronisering av filer till sekundär volym (SPOF)  
* RabbitMQ health checks och auto-restart  
* Pending-scan-fallback och notifiering till Admin  

### 6. Infrastruktur

* IaC med Terraform/Pulumi  
* Blue-Green/Canary deployment  

### 7. Notifieringar & Webhooks

* Skicka webhooks/mail vid scanning och karantän  

---

## Nuvarande Status

- **Backend** (FastAPI): Upload, List, Download, Admin Settings API ✔️  
- **RBAC & JWT**: Middleware och token-verifiering implementerat ✔️  
- **Worker**: ClamAV INSTREAM, statusuppdatering ✔️  
- **Infra**: Postgres, RabbitMQ, ClamAV, Docker Compose ✔️  
- **Admin UI scaffold**: Vite + React initierat, routing ✔️  
- **SettingsPage & UploadPage**: Implementerade och testade ✔️  

## Återstående Uppgifter

- [ ] Formulärvalidering och felhantering i SettingsPage och UploadPage (loading/spinner, error states)  
- [ ] Logotyp-upload: ny `POST /admin/logo` endpoint och UI-komponent  
- [ ] Retention cleanup-jobb i worker + toggle i UI  
- [ ] **Sekundär virusmotor**: integrera valfri alternativ scanningstjänst (VirusTotal API eller ClamAV multi-engine) som optional toggle  
- [ ] Enhetstester: backend (pytest) och frontend (Jest + React Testing Library)  
- [ ] Docker-image för Admin UI och uppdatera `docker-compose.yaml`  
- [ ] GitHub Actions: bygg, lint, test för backend och frontend  
- [ ] End-to-end-testflöden (upload → scan → toggle → download)  
- [ ] Slutgiltig dokumentation: `README.md`, API-spec, konfigurationsguide  
- [ ] Instrumentera observability:  
  - Lägg till Prometheus-metrics i FastAPI (`/metrics` endpoint)  
  - OpenTelemetry tracing för API och worker  
- [ ] Input-validering i backend:  
  - Kolla `file.content_type` och magic bytes vid upload  
  - Begränsa maximal filstorlek och skydd mot zip-bombs  
- [ ] Settings-cache:  
  - In-memory cache (t.ex. `lru_cache`) eller batch-hämtning av settings  
- [ ] Asynkrona förbättringar:  
  - Överväg `asyncpg` och `aio-pika` för skalbarhet  

## Nästa Steg

1. 🖼️ **Logotyp-upload**  
   - Backend: `POST /admin/logo`, spara URL i `settings.logo_url`  
   - Frontend: fil-input + live-preview i SettingsPage  
2. 🗑️ **Retention Cleanup**  
   - Worker: schemalägg rensning enligt `settings.cleanup_schedule`  
   - Frontend: toggle för `retention_enabled`  
3. 🧪 **Testautomation & CI**  
   - Skriv och kör enhetstester (pytest, Jest)  
   - Sätt upp GitHub Actions: bygg, lint, test för backend & frontend  
4. 📊 **Observability**  
   - Lägg till `/metrics`-endpoint med Prometheus-instrumentering  
   - Integrera OpenTelemetry i både API och worker  
5. 🛡️ **Input-validering & Säkerhet**  
   - Validera MIME-typ + magic bytes vid upload  
   - Begränsa maximal filstorlek  
6. ⚙️ **Cache & Async**  
   - Cachea settings med `lru_cache` eller batch-hämtning  
   - Utvärdera `asyncpg` + `aio-pika` för asynkrona anrop  
7. 🎯 **Release v0.1.0**  
   - Paketera Admin UI image, uppdatera Compose  
   - Tagga och publicera med changelog  

