# ADR 0006: Lieferung in die Landing Zone

- **Status:** Akzeptiert
- **Datum:** 2026-11-16
- **Ticket:** RB-105

## Kontext

Die Testdaten kommen in sechs Batches und liegen lokal als CSV- und JSONL-Dateien, je
Batch gegliedert nach Quellsystem (kasse, kunden, filialbestellungen, bestand, stammdaten).
Sie müssen einzeln und nacheinander in die Landing Zone (Volume `batches` im Schema
`eingang`) gebracht werden. Ein Batch darf nicht versehentlich doppelt geliefert werden,
und es muss abfragbar sein, was wann geliefert wurde.

## Entscheidung

- Das Lieferwerkzeug ist ein Kommandozeilenbefehl im Paket `redbricks`
  (`redbricks-liefern`) und läuft lokal, da die Dateien lokal liegen.
- Es nutzt das Databricks SDK für Python mit dem CLI-Profil `redbricks`.
- Ziel-Catalog, Schema-Namen und Warehouse liest es aus der aufgelösten Bundle-Konfiguration
  (`databricks bundle validate --output json`). Die Namen sind damit nur in der
  `databricks.yml` definiert.
- Ablage im Volume: `batches/<quelle>/<batch>/<datei>`. Auto Loader kann so je Quelle
  einen Ordner lesen, der Batch bleibt am Pfad erkennbar.
- Protokoll: Delta-Tabelle `lieferprotokoll` im Schema `betrieb`, eine Zeile je Datei mit
  Batch, Quelle, Datei, Zielpfad, Größe, SHA-256-Prüfsumme, Lieferzeitpunkt und Benutzer.
- Schutz vor Doppel-Lieferung, pro Datei (Schlüssel: Zielpfad):
  1. Dateien, die laut Protokoll schon geliefert sind, werden übersprungen.
  2. Der Upload überschreibt nie eine bestehende Datei.
  Ein abgebrochener Batch kann so gefahrlos erneut gestartet werden.
- Die Prüfsumme dient der Nachvollziehbarkeit, nicht dem Abweisen: Liefert eine Quelle
  dieselbe Datei unter anderem Namen noch einmal, wird sie geliefert. Wiederholungen zu
  erkennen ist Aufgabe der Verarbeitung, nicht der Anlieferung.
- Versteckte Dateien (z. B. `.DS_Store`) werden nicht geliefert.

## Betrachtete Alternativen

### Option A: Lokales CLI-Werkzeug mit Databricks SDK (gewählt)
- Vorteile:
  - Direkter Zugriff auf die lokalen Dateien
  - Testbar mit pytest, Teil des Pakets
- Nachteile:
  - Läuft nur dort, wo die Testdaten liegen

### Option B: Upload per `databricks fs cp` und Protokoll von Hand (verworfen)
- Vorteile:
  - Kein eigener Code
- Nachteile:
  - Kein Schutz vor Doppel-Lieferung, Protokoll fehleranfällig
- Grund für die Ablehnung: Erfüllt die Akzeptanzkriterien nicht verlässlich.

### Option C: Duplikatprüfung nur je Batch (verworfen)
- Vorteile:
  - Einfacher
- Nachteile:
  - Ein abgebrochener Batch könnte nicht fortgesetzt werden
- Grund für die Ablehnung: Prüfung je Datei ist robuster und genauso einfach abfragbar.

### Option D: Ablage `batches/<batch>/<quelle>/<datei>` (verworfen)
- Vorteile:
  - Entspricht der Lieferstruktur
- Nachteile:
  - Auto Loader müsste je Quelle mit Platzhaltern über alle Batch-Ordner lesen
- Grund für die Ablehnung: Ablage je Quelle passt besser zur Verarbeitung je Data Product.

## Konsequenzen

- Positiv: Jede Lieferung ist nachvollziehbar und wiederholbar, ohne Daten zu verdoppeln.
- Negativ: Das Werkzeug hängt von der Databricks CLI (für die Bundle-Konfiguration) und
  einem SQL Warehouse (für das Protokoll) ab.
- Folgemaßnahmen: RB-203 liest die Dateien je Quelle aus dem Volume; RB-402 nutzt das
  Werkzeug, um Testdaten in die Test-Landing-Zone zu liefern.