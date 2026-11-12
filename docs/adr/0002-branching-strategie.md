# ADR 0002: Branching-Strategie

- **Status:** Akzeptiert
- **Datum:** 2026-11-12
- **Ticket:** RB-101 (Bezug: RB-403, RB-404)

## Kontext

Ich entwickle das Projekt allein. Die Umgebungen Entwicklung, Test und Produktion
werden nicht über Branches getrennt, sondern über Targets im Databricks Bundle
(RB-102). Ab RB-404 soll nach jedem Merge nach `main` automatisch eine Pipeline
laufen: Unit Tests → Deploy in Test → Integrationstest → Deploy in Produktion.
Es braucht daher eine einfache Branching-Strategie, bei der jede Änderung vor
dem Merge geprüft wird und `main` jederzeit deploybar ist.

## Entscheidung

Es wird GitHub Flow verwendet:
- `main` ist immer deploybar.
- Für jedes Ticket gibt es einen kurzlebigen Branch nach dem Schema
  `feature/rb-<nr>-<kurzbeschreibung>`, z. B. `feature/rb-101-arbeitsumgebung`.
  Für Fehlerbehebungen optional `fix/rb-<nr>-<kurzbeschreibung>`.
- Änderungen kommen nur per Pull Request nach `main`.
- Nach dem Merge wird der Branch automatisch gelöscht.
- Commit-Nachrichten folgen den Conventional Commits
  (z. B. `feat: …`, `fix: …`, `docs: …`, `chore: …`).

## Betrachtete Alternativen

### Option A: GitHub Flow (gewählt)
- Vorteile:
  - Einfach, nur ein langlebiger Branch (`main`)
  - Passt zur Arbeit einer einzelnen Person
  - Passt zu Continuous Deployment: ein Merge nach `main` startet die CD-Pipeline (RB-404)
- Nachteile:
  - Lange offene Branches führen zu Merge-Konflikten, daher müssen Branches klein bleiben

### Option B: GitFlow mit `develop` (verworfen)
- Vorteile:
  - Geeignet für Software mit festen Release-Zyklen und mehreren parallelen Versionen
- Nachteile:
  - Bildet die Umgebungstrennung doppelt ab (Branches und Bundle-Targets)
  - Mehr Branches und Merges ohne Mehrwert für eine Einzelperson
- Grund für die Ablehnung: Die Umgebungen werden bereits über Bundle-Targets
  getrennt, und es gibt keine festen Releases. GitFlow würde nur Aufwand erzeugen.

### Option C: Direkt auf `main` committen (verworfen)
- Vorteile:
  - Am schnellsten, kein Pull Request nötig
- Nachteile:
  - Keine automatische Prüfung vor dem Merge, ungetesteter Code landet in `main`
- Grund für die Ablehnung: Ohne Pull Request hat die CI (RB-403) keinen
  Ansatzpunkt, und Fehler würden direkt bis in Produktion gelangen.

## Konsequenzen

- Positiv: Klarer, einfacher Ablauf. Jede Änderung ist über einen Pull Request
  nachvollziehbar und einem Ticket zugeordnet.
- Negativ: Für jede noch so kleine Änderung ist ein Branch und ein Pull Request nötig.
- Folgemaßnahmen:
  - In den Repo-Einstellungen ist „Automatically delete head branches“ aktiviert.
  - In RB-403 wird `main` per Branch-Ruleset geschützt: Mergen nur per Pull
    Request und nur mit grünen CI-Checks.
