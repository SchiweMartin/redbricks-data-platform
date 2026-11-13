# ADR 0004: Unity-Catalog-Struktur

- **Status:** Akzeptiert
- **Datum:** 2026-11-13
- **Ticket:** RB-103

## Kontext

Die Plattform braucht in Unity Catalog einen Ort für angelieferte Rohdateien (Landing Zone),
für technische Betriebsdaten (Lieferprotokoll, Qualitätsmesswerte) und für die Tabellen der
Data Products. Die Umgebungen dev, test und prod werden laut ADR 0003 über einen Catalog je
Umgebung getrennt, da es nur einen Workspace gibt. Welche Data Products es gibt, wird erst
in RB-201 entschieden.

## Entscheidung

Je Umgebung (`<env>` = dev, test, prod) gibt es einen Catalog `redbricks_<env>` mit:

| Schema | Objekt | Zweck | ab Ticket |
|---|---|---|---|
| `eingang` | Volume `batches` | Landing Zone: angelieferte Rohdateien (CSV, JSONL) | RB-103 / RB-105 |
| `betrieb` | Tabellen | Lieferprotokoll, Qualitätsmesswerte | RB-105 / RB-302 |
| `dp_<name>` | Tabellen | ein Schema je Data Product, Schicht als Tabellenpräfix | RB-201 ff. |

### Tatsächliche Schema-Namen (Präfix aus dem Bundle)

Schemas erhalten den Namenspräfix des Targets:

| Umgebung | Beispiel |
|---|---|
| dev | `redbricks_dev.dev_<benutzer>_eingang` |
| test | `redbricks_test.test_eingang` |
| prod | `redbricks_prod.prod_eingang` |

Der Wunsch, in dev auf den Benutzernamen zu verzichten, ist nicht umsetzbar: Die CLI
erzwingt im Modus `development` den Benutzernamen im Präfix. Code darf Schema-Namen daher
nie fest verdrahten, sondern bezieht sie über Bundle-Referenzen oder Variablen.

### Anlage

- **Catalogs** werden per SQL angelegt (`setup/catalogs.sql`, idempotent mit
  `IF NOT EXISTS`). Abweichung wegen Free Edition: Die REST-API, die das Bundle nutzt, kann
  in der Free Edition keine Catalogs mit Default Storage anlegen
  (Fehler `Metastore storage root URL does not exist`, 400 INVALID_STATE).
- **Schemas und Volumes** werden per Bundle angelegt (`resources/unity_catalog.yml`).
- Jedes Objekt hat einen Kommentar, der seinen Zweck beschreibt.
- In dev und test darf `bundle destroy` Schemas und Volumes abräumen. Der leere Catalog
  bleibt bestehen, da er nicht vom Bundle verwaltet wird.
- In prod sind Schemas und Volume mit `lifecycle.prevent_destroy` geschützt. Destroy und
  Deploys, die ein Objekt neu anlegen müssten, werden verweigert.
- Data-Product-Schemas werden nicht in RB-103 angelegt, sondern mit dem jeweiligen Data Product.

## Betrachtete Alternativen

### Option A: Landing Zone als Schema im Umgebungs-Catalog (gewählt)
- Vorteile:
  - Einfache Struktur: drei Catalogs, je Umgebung alles an einem Ort
  - Umgebungen bleiben vollständig getrennt, der Integrationstest (RB-402) hat eine
    eigene Landing Zone in `redbricks_test`
  - Rechte für die Anlieferung lassen sich auf Schema-Ebene vergeben
- Nachteile:
  - Rohdateien und verarbeitete Daten liegen im selben Catalog

### Option B: Eigener Landing-Zone-Catalog je Umgebung, z. B. `redbricks_lz_dev` (verworfen)
- Vorteile:
  - Strengere Trennung von Anlieferung und Verarbeitung auf Catalog-Ebene
  - Üblich in großen Organisationen mit eigenem Team für die Anlieferung
- Nachteile:
  - Doppelt so viele Catalogs, mehr Konfiguration
- Grund für die Ablehnung: Ohne eigenes Anlieferungs-Team bringt die zusätzliche Trennung
  keinen Nutzen. Bei wachsender Organisation neu bewerten.

### Option C: Eine gemeinsame Landing Zone für alle Umgebungen (verworfen)
- Vorteile:
  - Testdaten nur einmal ablegen
- Nachteile:
  - dev und test würden dieselben Dateien lesen wie prod, keine Isolation
- Grund für die Ablehnung: Widerspricht ADR 0003 und RB-402 (Integrationstest isoliert).

### Option D: Catalogs als Bundle-Ressource (verworfen)
- Vorteile:
  - Alles an einer Stelle, Destroy entfernt auch den Catalog
- Nachteile:
  - Funktioniert in der Free Edition nicht (Default Storage)
- Grund für die Ablehnung: Technisch nicht möglich. Bei einem Workspace mit eigenem
  Speicher neu bewerten.

## Konsequenzen

- Positiv: Klare, gleichförmige Struktur in allen Umgebungen. Neue Data Products bekommen
  nur ein eigenes Schema.
- Negativ: Catalogs müssen vor dem ersten Deploy per SQL angelegt werden. Schema-Namen
  unterscheiden sich je Umgebung durch den Präfix.
- Folgemaßnahmen:
  - README: Setup-Schritt „Catalogs anlegen“.
  - RB-404: `setup/catalogs.sql` vor dem Deploy in CI ausführen.
  - RB-105: Ordnerstruktur im Volume und Lieferprotokoll in `betrieb` anlegen.