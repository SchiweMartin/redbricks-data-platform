# Redbricks Data Platform

Lakehouse-Plattform für die fiktive Baumarktkette redbricks: Data Products,
Declarative Automation Bundles und CI/CD auf der Databricks Free Edition.
Darauf entstehen ein AI/BI-Dashboard für die Vertriebsleitung und eine
Databricks App mit Lakebase für die Marktleitungen.

## Voraussetzungen

- Databricks Free Edition Workspace
- GitHub-Account
- macOS mit Homebrew
- Databricks CLI ≥ v1.0

## Setup

1. **Repository klonen:** `git clone https://github.com/SchiweMartin/redbricks-data-platform.git`
2. **Databricks CLI installieren:** über Homebrew (`databricks/tap`), prüfen mit `databricks -v`.
3. **CLI anmelden (OAuth):** `databricks auth login --host <workspace-url> --profile redbricks`
4. **Anmeldung prüfen:** `databricks current-user me --profile redbricks`
5. **GitHub-Token erstellen:** Fine-grained Personal Access Token, nur für dieses
   Repository, Berechtigungen *Contents* und *Workflows* (Read and write), Ablauf 90 Tage.
6. **Token in Databricks hinterlegen:** Settings → Linked accounts → GitHub → Personal access token.
7. **Git-Folder anlegen:** Workspace → Home → Create → Git folder → Repository-URL eintragen.
8. **Catalogs anlegen** (einmalig): jede Anweisung aus `setup/catalogs.sql` ausführen, z. B.
   `databricks experimental aitools tools query "CREATE CATALOG IF NOT EXISTS redbricks_dev COMMENT '…'" --profile redbricks`
9. **Bundle prüfen:** `databricks bundle validate --target dev --profile redbricks`

> Alle CLI-Befehle in diesem Projekt immer mit `--profile redbricks` ausführen.

## Abweichungen wegen Free Edition

- **Git-Integration per PAT statt GitHub App:** Die Free Edition bietet für Git-Folder
  nur einen Personal Access Token an. Der Token ist auf dieses Repository und die
  minimal nötigen Rechte beschränkt und läuft nach 90 Tagen ab.
- **Catalogs per SQL statt per Bundle:** Die Free Edition kann Catalogs mit Default
  Storage nicht über die API anlegen, die das Bundle nutzt. Die Catalogs werden daher mit
  `setup/catalogs.sql` angelegt, Schemas und Volumes weiterhin per Bundle (siehe ADR 0004).

## Dokumentation

- Architekturentscheidungen (ADRs): [`docs/adr/`](docs/adr/)

## Hinweis

redbricks ist ein fiktives Unternehmen. Aufgabenbeschreibung und Testdaten sind
nicht Teil dieses Repositorys.
