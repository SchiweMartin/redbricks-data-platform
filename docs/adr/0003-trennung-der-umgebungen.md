# ADR 0003: Trennung der Umgebungen in einem Workspace

- **Status:** Akzeptiert
- **Datum:** 2026-11-12
- **Ticket:** RB-102

## Kontext

Das Projekt braucht die Umgebungen Entwicklung (dev), Test (test) und Produktion (prod).
Die Databricks Free Edition bietet nur einen Workspace. Die Umgebungen können sich daher
an vier Stellen gegenseitig stören: Dateien im Workspace, Namen von Jobs und Pipelines,
Daten in Unity Catalog und Ausführung (Identität, Zeitpläne). Zusätzlich erlaubt die
Free Edition nur eine aktive Pipeline je Pipeline-Typ und maximal 5 gleichzeitige Job-Tasks.

## Entscheidung

Die Umgebungen werden als drei Targets im Bundle abgebildet und auf allen vier Ebenen getrennt:

| Ebene | dev | test | prod |
|---|---|---|---|
| Modus | `development` | `production` | `production` |
| Dateien (root_path) | eigener Benutzerordner (Standard im Development-Modus) | `/Workspace/Shared/.bundle/redbricks/test` | `/Workspace/Shared/.bundle/redbricks/prod` |
| Namenspräfix | `[dev <benutzer>]` (automatisch) | `[test]` | `[prod]` |
| Daten (Catalog) | `redbricks_dev` | `redbricks_test` | `redbricks_prod` |
| Zeitpläne | pausiert (automatisch) | pausiert | aktiv |

Weitere Festlegungen:
- Der Workspace-Host ist in jedem Target fest eingetragen, damit nie in einen falschen
  Workspace deployt werden kann.
- Innerhalb eines Catalogs gibt es ein Schema je Data Product (`dp_<name>`). Die Schicht
  steht als Präfix im Tabellennamen (`raw_in_`, `bronze_`, `silver_`, `quarantine_`).
  Details folgen in RB-103.
- Test läuft im Modus `production`, damit der Integrationstest dasselbe Verhalten prüft,
  das später in Produktion gilt ("Test like you run").
- Pipelines laufen getriggert, nicht kontinuierlich. Die Umgebungen verarbeiten nacheinander,
  nie gleichzeitig.

## Betrachtete Alternativen

### Option A: Targets mit eigenem Catalog je Umgebung (gewählt)
- Vorteile:
  - Code ist in allen Umgebungen gleich, nur der Catalog wechselt über eine Variable
  - Berechtigungen und Aufräumen pro Catalog möglich
  - Test kann vollständig geleert werden, ohne Prod zu gefährden
- Nachteile:
  - Drei Catalogs müssen angelegt und gepflegt werden

### Option B: Ein Catalog mit Schemas je Umgebung (z. B. `dev_dp_kasse`) (verworfen)
- Vorteile:
  - Nur ein Catalog
- Nachteile:
  - Umgebung steckt in jedem Schema-Namen, Code muss Schema-Namen zusammensetzen
  - Rechte nur pro Schema steuerbar
- Grund für die Ablehnung: Schlechtere Trennung und mehr Logik im Code.

### Option C: Prod ohne Namenspräfix (Databricks-Standard) (verworfen)
- Vorteile:
  - Saubere Namen in Produktion
- Nachteile:
  - In einem gemeinsamen Workspace sind Prod-Ressourcen nicht auf einen Blick erkennbar
- Grund für die Ablehnung: Der Standard setzt einen eigenen Prod-Workspace voraus.

### Option D: Eigener Dev-Catalog je Entwickler (verworfen)
- Vorteile:
  - Mehrere Entwickler stören sich nicht
- Nachteile:
  - Zusätzliche Catalogs ohne Nutzen
- Grund für die Ablehnung: Es gibt nur einen Entwickler. Bei Teamwachstum neu bewerten.

## Konsequenzen

- Positiv: Ein Deploy in dev verändert weder Dateien, Ressourcen noch Daten von test und prod.
- Negativ: Wegen der Pipeline-Grenze kann immer nur eine Umgebung gleichzeitig verarbeiten.
- Folgemaßnahmen:
  - RB-103: Catalogs, Schemas und Volumes per Bundle anlegen und prüfen, ob der
    Namenspräfix auf Schemas wirkt.
  - RB-404: CD-Läufe gegen Parallelität absichern (z. B. Concurrency-Gruppe in GitHub Actions).
  - RB-404: Deploy nach test und prod mit eigener Identität statt persönlichem Benutzer prüfen.