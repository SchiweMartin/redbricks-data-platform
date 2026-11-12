# ADR 0004: Unity-Catalog-Struktur

- **Status:** Akzeptiert
- **Datum:** 2026-11-12
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

Weitere Festlegungen:
- Catalogs, Schemas und Volumes werden per Bundle angelegt (direct deployment engine).
- Jedes Objekt hat einen Kommentar, der seinen Zweck beschreibt.
- In dev und test darf `bundle destroy` alles abräumen. In prod ist der Catalog mit
  `prevent_destroy` gegen versehentliches Löschen geschützt.
- Data-Product-Schemas werden nicht in RB-103 angelegt, sondern mit dem jeweiligen Data Product.

## Betrachtete Alternativen

### Option A: Landing Zone als Schema im Umgebungs-Catalog (gewählt)
- Vorteile:
  - Einfache Struktur: drei Catalogs, je Umgebung alles an einem Ort
  - Umgebungen bleiben vollständig getrennt, der Integrationstest (RB-402) hat eine
    eigene Landing Zone in `redbricks_test.eingang`
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

## Konsequenzen

- Positiv: Klare, gleichförmige Struktur in allen Umgebungen. Neue Data Products bekommen
  nur ein eigenes Schema.
- Negativ: Rechte zwischen Anlieferung und Verarbeitung sind nur auf Schema-Ebene trennbar.
- Risiko: Falls die Free Edition keine eigenen Catalogs erlaubt, werden die Schemas im
  vorhandenen Catalog `workspace` mit Umgebungspräfix angelegt (Abweichung dokumentieren).
- Folgemaßnahmen: RB-105 legt die Ordnerstruktur im Volume und das Lieferprotokoll in
  `betrieb` an.