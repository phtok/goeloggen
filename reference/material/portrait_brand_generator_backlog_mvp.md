# Backlog: Brand Portrait Generator (MVP)

Stand: 2026-02-25  
Basis: `reference/material/portrait_brand_generator_pflichtenheft.md`

## Priorisierungslogik

- `P0`: Blocker fuer MVP-Launch
- `P1`: Wichtig fuer stabile Nutzbarkeit
- `P2`: Nachgelagert / Optimierung

## Epic 1: Plattformgrundlage (`P0`)

### Story 1.1 API Skeleton + Jobmodell
- Beschreibung: FastAPI Service mit Job-Lifecycle aufsetzen.
- Akzeptanzkriterien:
  - `POST /v1/jobs` erzeugt Job mit `job_id`.
  - `GET /v1/jobs/{job_id}` liefert Status (`queued`, `running`, `done`, `failed`).
  - Persistenz in PostgreSQL.

### Story 1.2 Objektstorage anbinden
- Beschreibung: Input/Output Images in R2 speichern.
- Akzeptanzkriterien:
  - Uploads landen in `inputs/{job_id}/`.
  - Varianten landen in `outputs/{job_id}/`.
  - Signed URL Zugriff fuer Frontend.

### Story 1.3 Queue + Worker Orchestrierung
- Beschreibung: Asynchrone Jobverarbeitung mit Redis Queue.
- Akzeptanzkriterien:
  - API schreibt Jobs in Queue.
  - Worker zieht Jobs und aktualisiert Status.
  - Retry fuer transient errors (max 2).

## Epic 2: Inputqualitaet und Preprocessing (`P0`)

### Story 2.1 Gesichtserkennung + Einzelface-Gate
- Beschreibung: Nur Bilder mit genau einem Gesicht akzeptieren.
- Akzeptanzkriterien:
  - 0 oder >1 Gesicht erzeugt validen Fehlercode.
  - Bounding Box wird gespeichert.

### Story 2.2 Qualitaetsscore berechnen
- Beschreibung: Score fuer Schaerfe, Belichtung, Framing.
- Akzeptanzkriterien:
  - API liefert Gesamt-Score und Einzelwerte.
  - Schwellwertregel fuer "Enhance empfohlen".

### Story 2.3 Optionales Preprocessing
- Beschreibung: Restore/Upscale/Normalize als Pipeline-Schritt.
- Akzeptanzkriterien:
  - Preprocessing per Job-Flag aktivierbar.
  - Vorher/Nachher Bildartefakte gespeichert.

## Epic 3: Inferenzpipeline (`P0`)

### Story 3.1 SDXL Basisintegration
- Beschreibung: Basisgenerierung mit fixem Seed-Management.
- Akzeptanzkriterien:
  - Job erzeugt drei Varianten.
  - Seeds werden persistiert.

### Story 3.2 Face-ID Einbindung
- Beschreibung: Identity-preserving Generation mit Face Adapter.
- Akzeptanzkriterien:
  - Identitaets-Score wird je Variante berechnet.
  - Unter Schwellwert markiert als "reject".

### Story 3.3 Brand-LoRA Integration
- Beschreibung: Laden und Anwenden der Brand-LoRA.
- Akzeptanzkriterien:
  - LoRA ist pro Brand-Profil konfigurierbar.
  - Versionsnummer wird in Metadaten gespeichert.

## Epic 4: Brand-Lock + Scoring (`P0`)

### Story 4.1 Brand-Config Runtime
- Beschreibung: JSON-Konfiguration fuer Brand-Regeln zur Laufzeit laden.
- Akzeptanzkriterien:
  - Aspect Ratio, Crop, Prompt-Template und LUT konfigurierbar.
  - Aenderungen ohne Code-Deploy moeglich.

### Story 4.2 Postprocessing + LUT
- Beschreibung: Einheitliches Color Grading anwenden.
- Akzeptanzkriterien:
  - Alle Varianten erhalten gleiches Finish.
  - Technischer Vergleich zeigt konsistente Farbraeume.

### Story 4.3 Brand-Score berechnen
- Beschreibung: Bildaehnlichkeit gegen Brand-Referenzset.
- Akzeptanzkriterien:
  - Score `0..1` je Variante.
  - Schwellenwert fuer "brand-konform" konfigurierbar.

## Epic 5: Frontend Workflow (`P1`)

### Story 5.1 Upload + Jobstatus UI
- Beschreibung: Single-Page Flow fuer Upload und Fortschritt.
- Akzeptanzkriterien:
  - Drag-and-drop Upload.
  - Live-Status inkl. Fehlermeldungen.

### Story 5.2 Variantenvergleich und Freigabe
- Beschreibung: Side-by-side Vergleich mit Scores.
- Akzeptanzkriterien:
  - 3 Varianten mit Score-Badges.
  - "Approve" setzt finale Variante.

### Story 5.3 Export UI
- Beschreibung: Download in Web- und Druckformat.
- Akzeptanzkriterien:
  - Exportbutton liefert gewuenschte Aufloesung.
  - Metadaten als JSON zugaenglich.

## Epic 6: Sicherheit, Audit, Betrieb (`P1`)

### Story 6.1 Rollen und Zugriff
- Beschreibung: Rollenmodell fuer Redaktion/Admin.
- Akzeptanzkriterien:
  - Nicht autorisierte Zugriffe werden blockiert.
  - Audit-Log fuer Freigabeaktionen vorhanden.

### Story 6.2 Datenloeschung
- Beschreibung: Lifecycle-Regeln fuer Rohbilder.
- Akzeptanzkriterien:
  - Automatische Loeschung nach konfigurierter Frist.
  - Loeschlauf wird protokolliert.

### Story 6.3 Monitoring + Alerts
- Beschreibung: Metriken und Alarme fuer Pipeline.
- Akzeptanzkriterien:
  - Dashboard fuer Laufzeit, Fehlerquote, Queue-Tiefe.
  - Alarm bei Fehlerquote > 5% (15 min).

## Epic 7: Modelltraining und Evaluation (`P1`)

### Story 7.1 Referenzset kuratieren
- Beschreibung: 80+ freigegebene Brand-Referenzbilder kuratieren.
- Akzeptanzkriterien:
  - Bildrechte dokumentiert.
  - Labelschema vollstaendig gepflegt.

### Story 7.2 Erste Brand-LoRA trainieren
- Beschreibung: Initialtraining mit dokumentierten Hyperparametern.
- Akzeptanzkriterien:
  - Modellartefakt versioniert gespeichert.
  - Eval-Report vorhanden.

### Story 7.3 A/B Evaluation
- Beschreibung: Baseline vs LoRA vergleichen.
- Akzeptanzkriterien:
  - Identitaets- und Brand-Score je Setup.
  - Entscheidung fuer Produktionsmodell dokumentiert.

## Vorschlag Sprintzuschnitt

- Sprint 1 (2 Wochen): Epic 1 + 2
- Sprint 2 (2 Wochen): Epic 3
- Sprint 3 (2 Wochen): Epic 4 + 5
- Sprint 4 (2 Wochen): Epic 6 + 7 + UAT

## Definition of Done (MVP)

- End-to-end Workflow funktioniert stabil:
  - Upload -> Qualitaetspruefung -> Generierung -> Auswahl -> Export
- Abnahmemetriken aus Pflichtenheft erreicht.
- Sicherheits- und Loeschkonzept aktiv.
- Monitoring und Alarmierung aktiv.
