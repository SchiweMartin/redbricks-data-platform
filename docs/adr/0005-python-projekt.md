# ADR 0005: Python-Projekt und Werkzeuge

- **Status:** Akzeptiert
- **Datum:** 2026-11-13
- **Ticket:** RB-104

## Kontext

Fachregeln (Geschäftstag, Beträge, Storno, Wareneinsatz …) sollen laut Aufgabe an genau
einer Stelle umgesetzt und getestet werden. Pipelines und Jobs sollen diesen Code
importieren, statt ihn in Notebooks zu wiederholen. Lint und Tests müssen lokal und später
in CI (GitHub Actions) identisch laufen. Databricks Serverless nutzt Python 3.12.

## Entscheidung

- Die Fachlogik liegt im Python-Paket `redbricks` im src-Layout (`src/redbricks/`).
- **uv** verwaltet Python-Version, virtuelle Umgebung und Abhängigkeiten.
  `uv.lock` wird committet, damit alle Umgebungen exakt dieselben Versionen nutzen.
- **Python 3.12** (`requires-python = ">=3.12,<3.13"`), passend zu Databricks Serverless.
- **ruff** als Linter und Formatierer (Regeln E, F, I, B, UP; Zeilenlänge 100).
- **pytest** als Testframework, Tests liegen in `tests/`.
- ruff und pytest sind Entwicklungsabhängigkeiten (`--dev`) und werden nicht in den
  Workspace deployt.
- Alle Befehle laufen über `uv run`, damit immer die Projektumgebung verwendet wird.

## Betrachtete Alternativen

### Option A: uv (gewählt)
- Vorteile:
  - Ein Werkzeug für Python-Version, Umgebung, Abhängigkeiten und Build
  - Sehr schnell, Lockfile für reproduzierbare Umgebungen
  - In den offiziellen Databricks-Bundle-Vorlagen verwendet
- Nachteile:
  - Vergleichsweise junges Werkzeug

### Option B: Poetry (verworfen)
- Vorteile:
  - Etabliert, ebenfalls mit Lockfile
- Nachteile:
  - Langsamer, Python-Version muss separat verwaltet werden (z. B. pyenv)
- Grund für die Ablehnung: Mehr Werkzeuge für dasselbe Ergebnis.

### Option C: pip mit requirements.txt (verworfen)
- Vorteile:
  - Keine zusätzlichen Werkzeuge
- Nachteile:
  - Kein echtes Lockfile, keine Trennung von Laufzeit- und Entwicklungsabhängigkeiten
- Grund für die Ablehnung: Keine reproduzierbaren Umgebungen.

### Option D: Fachlogik in Notebooks (verworfen)
- Vorteile:
  - Schneller Einstieg im Workspace
- Nachteile:
  - Schwer testbar, Logik wird zwischen Notebooks kopiert
- Grund für die Ablehnung: Widerspricht der Anforderung, Fachregeln an genau einer Stelle
  umzusetzen und zu testen.

## Konsequenzen

- Positiv: Fachregeln sind einmal implementiert, lokal testbar und überall importierbar.
- Negativ: Das Paket muss in den Workspace gebracht werden (Wheel oder Quellcode).
- Folgemaßnahmen:
  - RB-203: Import des Pakets in einer Pipeline im Workspace nachweisen.
  - RB-401: Unit Tests mit lokaler SparkSession (pyspark) ergänzen.
  - RB-403: `uv run ruff check .` und `uv run pytest` in GitHub Actions.