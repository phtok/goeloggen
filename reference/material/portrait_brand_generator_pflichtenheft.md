# Pflichtenheft: Brand Portrait Generator (MVP)

Stand: 2026-02-25  
Status: Konzeptionsphase, v0.1

## 1. Zielbild

Es soll ein Tool entstehen, das aus einem beliebigen Portraetfoto ein stark brand-konsistentes Portraet erzeugt, ohne die Identitaet der Person zu verlieren.

Kernnutzen:
- Konsistenter visueller Markenauftritt ueber Teams und Kanaele.
- Stark reduzierte manuelle Bildbearbeitung.
- Reproduzierbare Ergebnisse durch versionierte Presets.

## 2. Scope

### 2.1 In Scope (MVP)
- Upload eines einzelnen Portraetfotos (`jpg`, `jpeg`, `png`, `webp`).
- Automatische Bildqualitaetspruefung (Gesicht sichtbar, Schaerfe, Belichtung, Aufloesung).
- Optionale Bildverbesserung vor der Generierung.
- Identitaetserhaltende KI-Generierung in einem festen Brand-Look.
- Ausgabe von 1 Hauptvariante + 2 Alternativen.
- Export in mehreren Formaten (Web + Druck).
- Technische Nachvollziehbarkeit (Prompt/Seed/Modellversion als Metadaten).

### 2.2 Out of Scope (MVP)
- Gruppenfotos.
- Full-Body-Generierung.
- Video.
- Mehrmarken-Mandantenfaehigkeit.
- Oeffentliche Self-Service-Plattform.

## 3. Zielgruppen und Rollen

- `Redaktion/Marketing`: erstellt und waehlt finale Portraets.
- `Brand-Verantwortliche`: definieren und pflegen den Brand-Look.
- `Admin/ML-Ops`: betreiben Pipeline, Modelle und Monitoring.

## 4. Erfolgsmetriken (Abnahme)

- Identitaetsaehnlichkeit (`ArcFace Cosine`) >= 0.80
- Brand-Score (`CLIP gegen Brand-Referenzset`) >= 0.85
- Anteil Bilder ohne manuelle Nachbearbeitung >= 90%
- P95 Laufzeit pro Job <= 20 Sekunden (GPU-Inferenz)
- Fehlerquote technischer Jobs <= 2%

## 5. Funktionale Anforderungen

### FR-01 Upload und Vorpruefung
- System akzeptiert Einzelbilder bis 20 MB.
- System erkennt, ob genau ein Gesicht vorhanden ist.
- Bei Verstoessen liefert System klare Fehlermeldungen mit Korrekturhinweisen.

### FR-02 Qualitaets-Score
- Fuer jedes Inputbild wird ein Score (`0-100`) berechnet:
  - Schaerfe
  - Belichtung
  - Gesichtsgroesse im Frame
  - Blickrichtung
- Unter Schwellwert wird eine automatische Verbesserung angeboten.

### FR-03 Preprocessing
- Optionale Schritte:
  - Face Restore
  - Rauschreduktion
  - Leichte Super-Resolution
  - Farbnormalisierung
- Jeder Schritt wird im Job-Protokoll gespeichert.

### FR-04 Brand-Profil Auswahl
- Nutzer waehlt genau ein Brand-Profil (MVP: ein aktives Profil).
- Brand-Profil definiert:
  - Farbwelt
  - Lichtcharakter
  - Hintergrundtyp
  - Bildausschnitt/Headroom
  - Kleidungstonalitaet
  - Unerwuenschte visuelle Elemente

### FR-05 Identitaetserhaltende Generierung
- Generierung muss Face-ID-Embedding verwenden.
- Ergebnis muss in Gesichtszuegen eindeutig zur Inputperson passen.
- Generiert werden drei Varianten pro Job mit festem Variantenabstand.

### FR-06 Brand-Lock und Finish
- Nach der Generierung werden harte Brand-Regeln erzwungen:
  - Seitenverhaeltnis (z. B. `4:5` als Default)
  - Kopfposition
  - Hintergrundfamilie
  - Farb-LUT / Color Grading
- Verstoss gegen Regeln wird mit Quality Gate markiert.

### FR-07 Bewertung und Auswahl
- Pro Variante zeigt UI:
  - Identitaets-Score
  - Brand-Score
  - Qualitaets-Flags
- Nutzer kann Variante freigeben oder neu generieren.

### FR-08 Export
- Exportformate:
  - Web: `1200x1500`, `jpeg/webp`
  - Druck: `3000x3750`, `png/tiff` (optional)
- Metadatenfelder:
  - `job_id`
  - `seed`
  - `model_version`
  - `brand_profile_version`
  - `created_at`

### FR-09 Audit und Reproduzierbarkeit
- Jeder Job ist reproduzierbar ueber gespeicherte Parameter.
- Versionswechsel an Modellen/Profilen wird historisiert.

## 6. Nicht-funktionale Anforderungen

- Verfuegbarkeit Backend: >= 99.5% (Business Hours)
- API Antwortzeit (ohne Inferenz): P95 <= 300 ms
- Datenschutz:
  - Speicherbegrenzung und Loeschkonzept fuer Rohbilder
  - Rollenbasierte Zugriffe
  - Verschluesselung at-rest + in-transit
- Wartbarkeit:
  - Konfigurierbares Brand-Profil ohne Codeaenderung
  - Strukturierte Logs + Dashboards

## 7. Technische Zielarchitektur (MVP)

### 7.1 Komponenten
- `Frontend`: Next.js Upload- und Review-UI
- `API`: FastAPI (Job-Anlage, Status, Export)
- `Queue`: Redis + Worker
- `Inference Worker`: Python, Diffusers Pipeline
- `Model Layer`:
  - SDXL Basismodell
  - Face-ID Adapter (InstantID/IP-Adapter FaceID)
  - Brand-LoRA
- `Storage`: Cloudflare R2 (Inputs/Outputs/Artefakte)
- `DB`: PostgreSQL (Jobs, Scores, Versionen, Audit)

### 7.2 Datenfluss
1. Upload startet Job.
2. Precheck + Qualitaetsbewertung.
3. Optionales Preprocessing.
4. Inferenz mit Face-ID + Brand-LoRA.
5. Brand-Lock/Postprocessing.
6. Scoring und Varianten-Preview.
7. Freigabe und Export.

## 8. Brand-Config Schema (Beispiel)

```json
{
  "id": "goe_brand_v1",
  "aspect_ratio": "4:5",
  "crop": { "headroom_pct": 12, "eye_line_pct": 42 },
  "palette": ["#D9C7A1", "#F4EFE5", "#2E2A25"],
  "background_modes": ["soft_gradient", "neutral_studio"],
  "lighting": "soft_key_left",
  "prompt_template": "...",
  "negative_prompt": "...",
  "grading_lut": "goe_portrait_v1.cube",
  "forbidden_elements": ["busy_patterns", "hard_shadow_chin"]
}
```

## 9. Modell- und Datenanforderungen

### 9.1 Trainingsdaten fuer Brand-LoRA
- 50 bis 200 freigegebene Referenzportraets im Ziel-Look.
- Einheitliche Label-Konventionen:
  - Lichttyp
  - Hintergrundklasse
  - Framingklasse
  - Farbtemperatur

### 9.2 Datenqualitaet
- Nur rechtlich freigegebene Bilder mit Nutzungseinwilligung.
- Entfernen von Dubletten und Ausreissern vor Training.

### 9.3 Evaluation
- Holdout-Set mit interner manueller Brand-Bewertung.
- A/B Vergleich gegen Baseline ohne Brand-LoRA.

## 10. API-Schnittstellen (MVP, Entwurf)

- `POST /v1/jobs`
  - Erstellt Job mit Inputbild und Brand-Profil.
- `GET /v1/jobs/{job_id}`
  - Liefert Status und Zwischenergebnisse.
- `GET /v1/jobs/{job_id}/variants`
  - Liefert Varianten inkl. Scores.
- `POST /v1/jobs/{job_id}/approve`
  - Markiert finale Variante.
- `GET /v1/jobs/{job_id}/export`
  - Liefert Exportdateien und Metadaten.

## 11. Betriebs- und Monitoringkonzept

- Metriken:
  - Queue-Tiefe
  - GPU-Auslastung
  - Laufzeit je Pipeline-Schritt
  - Score-Verteilungen
  - Fehlerursachen nach Kategorie
- Alerting:
  - Fehlerquote > 5% fuer 15 Minuten
  - P95 Laufzeit > 30 Sekunden fuer 30 Minuten
- Logging:
  - Korrelations-ID pro Job
  - Strukturierte JSON-Logs

## 12. Sicherheits- und Compliance-Anforderungen

- Zugriff nur per Authentifizierung und Rollenmodell.
- Rohbilder standardmaessig automatische Loeschung nach 30 Tagen (konfigurierbar).
- Ausgabebilder behalten, solange fachlich erforderlich.
- Export von personenbezogenen Daten nur mit Berechtigung.
- Trainingsdaten und Inferenzdaten logisch getrennt.

## 13. Umsetzungsplan (8 Wochen, Vorschlag)

- Woche 1:
  - Brand-Workshop
  - Referenzsammlung
  - Finales Brand-Config Schema
- Woche 2:
  - API + Jobmodell + Storage-Grundlage
  - UI Upload + Status
- Woche 3:
  - Precheck + Preprocessing Pipeline
- Woche 4:
  - Inferenzpipeline mit Face-ID (ohne LoRA)
- Woche 5:
  - Erste Brand-LoRA trainieren
  - Brand-Lock integrieren
- Woche 6:
  - Scoring (Identitaet + Brand)
  - Variantenvergleich im UI
- Woche 7:
  - Export, Audit, Rechtekonzept
  - Last-/Stabilitaetstests
- Woche 8:
  - UAT
  - Go-Live MVP intern

## 14. Hauptrisiken und Gegenmassnahmen

- Risiko: Identitaet driftet bei starkem Stil.
  - Massnahme: Harte Identity-Schwelle + Auto-Reject.
- Risiko: Brand-Look nicht stabil ueber unterschiedliche Inputs.
  - Massnahme: Mehr diverse Trainingsdaten + striktere Brand-Locks.
- Risiko: Laufzeiten zu hoch.
  - Massnahme: Caching, optimierte Scheduler, ggf. kleinere Modelle fuer Previews.
- Risiko: Rechtliche Unsicherheit bei Trainingsbildern.
  - Massnahme: Datenfreigabeprozess mit dokumentierter Einwilligung.

## 15. Offene Produktentscheidungen (jetzt priorisieren)

1. Inferenzbetrieb:
   - A: Eigene GPU-Umgebung
   - B: Externer Inferenzdienst
2. Freigabeprozess:
   - A: Nur Redaktion
   - B: Redaktion + Brand-Owner Double-Check
3. Datenhaltung Rohbilder:
   - A: 30 Tage
   - B: 7 Tage
4. Zielausgabe MVP:
   - A: Nur `4:5`
   - B: `4:5` + `1:1`

## 16. Konkrete naechste Schritte

1. Brand-Referenzset (mind. 80 Bilder) final kuratieren.
2. Brand-Config v1 gemeinsam freigeben.
3. Architekturentscheidung fuer Inferenzbetrieb treffen.
4. Umsetzung Ticket-Backlog aus diesem Dokument ableiten.
