# PROJEKTÖVERSIKT

Detta dokument ger en översikt över FILES-projektet, dess syfte, nyckelfunktioner samt planerade milstolpar.

## Ändamål

FILES är en webbaserad lösning för att tillåta användare att:

* Ladda upp filer för virusskanning.
* Utföra checksum-kontroll (t.ex. MD5, SHA256).
* Visa detaljerade resultat och rapporter för både virusskanning och checksums.

Lösningen är designad för hög skalbarhet, modulär utbyggnad och kan integreras med extern autentisering (AD SSO) när RBAC är aktiverat.

## Nyckelfunktioner

1. **Användardel (Web UI)**

   * Förenklad uppladdning av filer.
   * Realtidsstatus för skanning.
   * Visning av checksumvärden.
2. **Admin-del (Web Admin UI)**

   * Konfiguration av skanningsmotorer och algoritmer.
   * Hantering av användare och RBAC.
   * Systemövervakning och statistik.
3. **Backend API**

   * Endpoints för att initiera och hämta resultatuppgifter.
   * Asynkron orkestrering via RabbitMQ.
4. **Worker-tjänster**

   * Virusworker: Primär virusskanning med ClamAV.
   * Checksum-worker: Sekventiell beräkning av checksums.
   * Valfri sekundär virusskanning som verifieringssteg.

## Skalbarhet

* Horisontell skalning av Backend bakom lastbalanserare.
* RabbitMQ-klustring för hög tillgänglighet.
* Multipla instanser av Workers.
* Databasreplikering för prestanda och redundans.

## Roadmap

| Milstolpe                    | Status      | Beskrivning                                                |
| ---------------------------- | ----------- | ---------------------------------------------------------- |
| Projektinitiering            | ✅ Klar      | Grundläggande projektstruktur och dokumentation etablerad. |
| Grundläggande API            | ✅ Klar      | `POST /scan` och `GET /scan/{id}` implementerat.           |
| Virusscanning                | ✅ Klar      | ClamAV-integration via virusworker.                        |
| Checksum-kontroll            | ✅ Klar      | MD5 och SHA256 beräknas av checksum-worker.                |
| Sekventiell verifierskanning | 🚧 Pågående | Optionell sekundär skanning implementeras.                 |
| Admin UI                     | 🚧 Pågående | Design och utveckling av admin-panel för konfiguration.    |
| Metrics & Observability      | 🟩 Planerad | Integrera Prometheus och Grafana för systemövervakning.    |
| Autentisering & RBAC         | 🟩 Planerad | AD SSO som stödfunktion när RBAC aktiveras.                |
| CI/CD-pipeline               | 🟩 Planerad | GitHub Actions för lint, test, build och deployment.       |
| Dokumentuppdatering          | 🟩 Planerad | Synkronisera dokument (README, PROJECT, architecture).     |

---

*Datum: 2025-06-24*
