# ADR 0001: Öffentliches GitHub-Repository

- **Status:** Akzeptiert
- **Datum:** 2026-11-12
- **Ticket:** RB-101

## Kontext

Das Projekt wird mit GitHub Free umgesetzt. Für spätere Tickets (RB-403, RB-404)
werden CI/CD mit GitHub Actions, Branch-Schutz für `main` und eine Freigabe vor
dem Deploy in Produktion benötigt. GitHub Free bietet Branch-Schutz und
Environment-Freigaben nur für öffentliche Repositories. Private Repositories
haben zudem nur 2.000 Actions-Minuten pro Monat.

## Entscheidung

Das Repository wird öffentlich geführt, weil nur so alle benötigten
CI/CD-Funktionen in GitHub Free kostenlos verfügbar sind.

## Betrachtete Alternativen

### Option A: Öffentliches Repository (gewählt)
- Vorteile:
  - Unbegrenzte GitHub-Actions-Minuten
  - Branch-Schutz und Environment-Freigaben verfügbar
  - Secret Scanning und Push Protection kostenlos
  - Projekt kann als Portfolio gezeigt werden
- Nachteile:
  - Code, Commits und Historie sind für jeden sichtbar
  - Höheres Risiko, falls versehentlich Secrets committet werden

### Option B: Privates Repository (verworfen)
- Vorteile:
  - Inhalte sind nicht öffentlich sichtbar
- Nachteile:
  - Nur 2.000 Actions-Minuten pro Monat
  - Kein Branch-Schutz und keine Environment-Freigaben
- Grund für die Ablehnung: Ohne Branch-Schutz kann technisch nicht
