# ADR 0009: Umgang mit Schemaänderungen und unsauberen Werten in Bronze

- **Status:** Akzeptiert
- **Datum:** 2026-11-20
- **Ticket:** RB-204

## Kontext

Die Quellsysteme können ohne Ankündigung neue Felder schicken („neue Kassensoftware“),
Werte in falschem Format liefern und technisch kaputte Datensätze erzeugen. Bronze soll
roh und vollständig bleiben: Kein Datensatz darf verloren gehen. Fehlerhafte Werte sollen
erst in Silver erkannt und behandelt werden.

## Entscheidung

### Lesen in Bronze (Auto Loader)

- **Keine Typ-Inferenz** (`cloudFiles.inferColumnTypes = false`): Alle Spalten werden als
  `STRING` gespeichert, verschachtelte Strukturen (z. B. `positionen`) als JSON-Text.
  Typumwandlung und Validierung erfolgen in Silver.
- **Schema-Evolution `addNewColumns`** (`cloudFiles.schemaEvolutionMode`): Neue Felder
  werden zu neuen Spalten. Der betroffene Flow stoppt, das Update wird abgebrochen und
  automatisch mit dem neuen Schema neu gestartet (`cause: SCHEMA_CHANGE`).
- **Rescued Data:** Die Spalte `_rescued_data` fängt Werte auf, die nicht ins Schema passen
  (z. B. abweichende Groß-/Kleinschreibung), inklusive Quelldatei.
- Beide Optionen sind ausdrücklich im Code gesetzt, obwohl sie dem Standard entsprechen.

### Absicherungen

1. Silver wählt seine Spalten ausdrücklich aus (kein `select("*")`). Neue Bronze-Spalten
   ändern Silver und den Data Contract nur durch bewusste Entscheidung.
2. Zeilen mit Inhalt in `_rescued_data` und technisch kaputte Zeilen (`event_id IS NULL`)
   werden als Qualitätskriterium gemessen (RB-302) und in Silver in Quarantäne genommen (RB-303).
3. Dateien in der Landing Zone werden nie gelöscht oder verändert. Der Rohinhalt kaputter
   Zeilen ist dort jederzeit nachlesbar.
4. Jobs, die Pipelines starten, werten einen Abbruch wegen `SCHEMA_CHANGE` nicht als
   Fehlschlag (RB-205).

### Bekannte Einschränkung

Die Schema-Inferenz braucht mindestens eine Datei je Tabelle. In einer frischen Umgebung
scheitert der erste Lauf sonst mit `CF_EMPTY_DIR_FOR_SCHEMA_INFERENCE`. Testdaten enthalten
deshalb immer alle Dateiarten einer Quelle (z. B. Bons und Z-Bon).

## Testergebnis

Test mit eigenen Testdaten in der Umgebung test (Beschreibung: `tests/daten/schema/README.md`):

| Testfall | Zeile | Ergebnis in `bronze_bons` |
|---|---|---|
| neues Feld `kanal` | T02-0001 | neue Spalte `kanal`, Update automatisch neu gestartet; alte Zeilen `NULL` |
| `markt_id = "Kiel"` | T02-0002 | als Text in `markt_id` gespeichert, kein Fehler |
| `Bon_Summe` statt `bon_summe` | T02-0003 | `bon_summe` leer, Wert mit Quelldatei in `_rescued_data` |
| abgeschnittene Zeile | T02-0004 | Zeile mit `NULL`-Werten, Quelldatei in `_quelle_datei` |

Alle 6 Testzeilen sind in Bronze angekommen. Kein Datensatz ging verloren.

## Betrachtete Alternativen

### Option A: Strings, `addNewColumns`, Rescued Data (gewählt)
- Vorteile: nichts geht verloren, neue Felder sind sofort nutzbar, Bronze bleibt roh
- Nachteile: ein abgebrochenes und neu gestartetes Update bei jeder Schemaänderung

### Option B: `rescue` (verworfen)
- Vorteile: stabiles Schema, kein Abbruch
- Nachteile: neue Felder sind im JSON-Text von `_rescued_data` versteckt
- Grund für die Ablehnung: Neue Felder wären schwer auswertbar.

### Option C: `failOnNewColumns` (verworfen)
- Vorteile: jede Änderung wird von einem Menschen freigegeben
- Nachteile: die Anlieferung steht, bis jemand reagiert
- Grund für die Ablehnung: Die Kassen schicken neue Felder ohne Ankündigung.

### Option D: Typ-Inferenz oder fest vorgegebenes Schema in Bronze (verworfen)
- Vorteile: typisierte Spalten schon in Bronze; mit festem Schema läuft auch eine leere Umgebung
- Nachteile: Falsche Werte führen zu Fehlern oder landen schon in Bronze in `_rescued_data`;
  das Schema muss von Hand gepflegt werden
- Grund für die Ablehnung: Bronze soll roh bleiben; Prüfung gehört nach Silver.

## Konsequenzen

- Positiv: Bronze ist vollständig und robust gegenüber Änderungen der Quellen.
- Negativ: Silver muss alle Typumwandlungen und Prüfungen leisten.
- Folgemaßnahmen: RB-205 (Abbruch wegen Schemaänderung im Job berücksichtigen),
  RB-301 bis RB-303 (Typumwandlung, Qualitätskriterien, Quarantäne).