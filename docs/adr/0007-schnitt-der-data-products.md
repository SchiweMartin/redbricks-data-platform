# ADR 0007: Schnitt der Data Products

- **Status:** Akzeptiert
- **Datum:** 2026-11-16
- **Ticket:** RB-201

## Kontext

redbricks liefert Daten aus fünf Quellsystemen: Kasse (Bons, Z-Bon), CRM, Lagerverwaltung,
Bestandsmeldung der Märkte und Warenwirtschaft (Artikel, Lieferanten, Märkte, Feiertage).
Daraus entstehen ein Dashboard für die Vertriebsleitung (Use Case 1) und eine App für die
Marktleitungen mit Nachschubvorschlägen (Use Case 2). Die Daten sollen als Data Products
mit Owner und Contract bereitgestellt werden. Vorgabe: höchstens vier Data Products, um
Aufwand und Free-Edition-Grenzen (eine aktive Pipeline je Typ) beherrschbar zu halten.

## Entscheidung

### Data Products

| Data Product | Schema | Owner (Rolle) | Quellen |
|---|---|---|---|
| Verkauf | `dp_verkauf` | Vertrieb | Kasse: Bons (`pos_*.jsonl`), Z-Bon (`kassenabschluss_*.csv`) |
| Kunde | `dp_kunde` | Kundenmanagement | CRM (`crm_*.jsonl`) |
| Stammdaten | `dp_stammdaten` | Warenwirtschaft | Artikel, Lieferanten, Märkte, Feiertage |
| Warenfluss | `dp_warenfluss` | Logistik und Disposition | Lagerverwaltung (`wms_*.jsonl`), Bestand (`bestand_*.csv`) |

Zusätzlich, ohne eigenes Data Product:
- **Semantic Layer** (Schema `kennzahlen`, Owner Controlling): Metric Views über den
  veröffentlichten Tabellen aller Data Products, Grundlage für Use Case 1.
- **Betrieb** (Schema `betrieb`, Owner Plattformteam): Lieferprotokoll und Qualitätsmessungen.

### Lademuster je Quelle

| Quelle | Lieferung laut Quellsystem | Lademuster | Data Product |
|---|---|---|---|
| Kasse: Bons | nur neue Events, nie Korrekturen | Append-only | Verkauf |
| Kasse: Z-Bon | eine Datei je Geschäftstag | Append-only | Verkauf |
| CRM | Änderungsprotokoll mit `_op` (I/U/D) und `_seq` | CDC | Kunde |
| Lagerverwaltung | Änderungsprotokoll mit `_op` (I/U/D) und `_seq` | CDC | Warenfluss |
| Bestand | nur neue Meldungen | Append-only | Warenfluss |
| Artikel, Lieferanten, Märkte, Feiertage | immer der komplette Export | Full Load | Stammdaten |

Damit sind alle geforderten Lademuster abgedeckt: Full Load (Stammdaten), Append-only
(Verkauf) und CDC (Kunde).

### Veröffentlichung

Jedes Data Product veröffentlicht seine Silver-Tabellen (Präfix `silver_`), Warenfluss
zusätzlich die Nachschub-Tabellen (Präfix `gold_`). Bronze- und Quarantäne-Tabellen sind
intern. Was veröffentlicht wird, beschreibt je Data Product ein Data Contract (RB-304).

| Data Product | Veröffentlicht (geplant) |
|---|---|
| Verkauf | `silver_bon`, `silver_bon_position`, `silver_kassenabschluss` |
| Kunde | `silver_kunde`, `silver_kunde_historie` (SCD 2), `silver_kundenkarte` |
| Stammdaten | `silver_artikel_historie` (SCD 2), `silver_lieferant`, `silver_markt`, `silver_lager`, `silver_oeffnungstag` |
| Warenfluss | `silver_bestellung`, `silver_bestand`, `gold_nachschubvorschlag`, `gold_nachschubentscheidung` |

### Abhängigkeiten

- Verkauf, Kunde und Stammdaten sind voneinander unabhängig.
- Warenfluss nutzt für die Nachschubvorschläge die veröffentlichten Tabellen von Verkauf
  (Absatz) und Stammdaten (aktive Artikel, VPE, Öffnungstage).
- Der Semantic Layer liest die veröffentlichten Tabellen aller Data Products.
- Data Products greifen nie auf interne Tabellen anderer Data Products zu.
- Verknüpfungen über Data Products hinweg (Kunde am Bon, Einkaufspreis am Geschäftstag)
  entstehen im Semantic Layer, nicht in den quellnahen Data Products.

## Betrachtete Alternativen

### Option A: Vier fachliche Data Products plus Semantic Layer (gewählt)
- Vorteile:
  - Überschaubare Zahl, jedes Lademuster mindestens einmal vertreten
  - Quellnahe Data Products bleiben unabhängig
- Nachteile:
  - Stammdaten vereint zwei fachliche Verantwortliche (Einkauf, Filialorganisation)
  - Warenfluss enthält mit dem Nachschub auch ein nutzerorientiertes Ergebnis und hängt
    dadurch von Verkauf und Stammdaten ab

### Option B: Feiner Schnitt mit sieben Data Products (verworfen)
Sortiment und Standort getrennt, Nachschub und Kennzahlen als eigene Data Products.
- Vorteile:
  - Klarere Verantwortung je Data Product
- Nachteile:
  - Deutlich mehr Aufwand für Pipelines, Contracts und Tests
- Grund für die Ablehnung: Überschreitet die Vorgabe von höchstens vier Data Products.

### Option C: Ein Data Product je Quellsystem (verworfen)
- Vorteile:
  - Einfache Zuordnung
- Nachteile:
  - Schneidet nach Technik statt nach Fachlichkeit; Bestand und Bestellungen gehören
    fachlich zusammen, stammen aber aus verschiedenen Systemen
- Grund für die Ablehnung: Data Products sollen fachlich geschnitten sein.

### Option D: Quellnahe Data Products verknüpfen sich gegenseitig (verworfen)
Zum Beispiel ordnet Verkauf den Kunden am Bon selbst zu.
- Vorteile:
  - Fertig angereicherte Tabellen direkt im Data Product
- Nachteile:
  - Abhängigkeiten zwischen quellnahen Data Products; eine Änderung beim Kunden würde
    Verkauf neu berechnen lassen
- Grund für die Ablehnung: Widerspricht der losen Kopplung über veröffentlichte Tabellen.

## Konsequenzen

- Positiv: Klarer Schnitt, jedes Data Product kann mit dem Blueprint (RB-501) gebaut werden.
- Negativ: Der Semantic Layer trägt die Verknüpfungslogik und wird dadurch umfangreicher.
- Folgemaßnahmen:
  - RB-202: erstes Data Product auswählen.
  - Schemas `dp_*` und `kennzahlen` werden mit dem jeweiligen Data Product per Bundle angelegt.
  - Free Edition: Die Pipelines der Data Products laufen nacheinander, orchestriert von
    einem Job (RB-205).