# FILES Project

Det här projektet är en filhanteringslösning med asynkron virus­sökning via RabbitMQ och ClamAV.

<!-- Sektion: Förutsättningar -->

## Förutsättningar

* **Windows**: PowerShell eller CMD
* **Docker & Docker Compose** (minst version 1.29)
* **Git**

<!-- Sektion: Klona & konfigurera miljö -->

## Kom igång

1. **Klona repot**:

   ```powershell
   git clone https://<repo-url>.git
   cd FILES-main
   ```
2. **Kopiera miljöfil** (hemligheter ska aldrig checkas in):

   ```powershell
   copy .env.example .env
   ```
3. **Redigera `.env`** för att sätta dina värden (t.ex. `DB_HOST`, `JWT_SECRET`):

   ```text
   # Exempel:
   # POSTGRES_USER=files_user
   # POSTGRES_PASSWORD=superhemligt
   # JWT_SECRET=byt-denna-till-en-säker-nyckel
   ```
4. **Starta alla tjänster** med Docker Compose:

   ```powershell
   docker-compose up -d
   ```

<!-- Sektion: Åtkomstpunkter -->

## Åtkomstpunkter

* **Backend API**: `http://localhost:8000`
* **Admin UI**: `http://localhost:3000`

<!-- Sektion: Projektstruktur för snabb överblick -->

## Projektstruktur

* `backend/` – FastAPI-app + databasinitiering
* `workers/` – RabbitMQ-konsument för virus­skanning
* `frontend/` – React/Vite-admin­gränssnitt
* `infra/` – Infrastruktur­konfiguration (tom för närvarande)
* `docs/` – Övrig dokumentation (arkitektur, API-kontrakt)

<!-- Sektion: Tester och kodkvalitet -->

## Tester & CI

Tester finns ännu inte, men följande rekommenderas:

1. **Backend**:

   ```powershell
   cd backend
   pytest
   ```
2. **Worker**:

   ```powershell
   pytest workers/
   ```

Lägg till GitHub Actions-workflow för:

* Linting (`flake8`)
* Typkontroll (`mypy`)
* Tester (`pytest`)

<!-- Sektion: Bidra -->

## Bidra

* **Branch-namn**: `feature/<namn>` eller `bugfix/<namn>`
* **Kodstil**: Använd `flake8`, `mypy` och skriv enhetstester.

<!-- Sektion: Licens -->

## Licens

Detta projekt är licensierat under **MIT License**.
