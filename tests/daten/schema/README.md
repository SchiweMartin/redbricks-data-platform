# Test: Schemaänderungen und unsaubere Werte in Bronze

Prüft, wie `bronze_bons` auf neue Felder, falsche Werte und kaputte Zeilen reagiert (RB-204).

## Testdaten

| Batch | Datei | Inhalt |
|---|---|---|
| `batch_t01_normal` | `kasse/pos_t01.jsonl` | 2 saubere Bons (T01-0001, T01-0002) |
| `batch_t01_normal` | `kasse/kassenabschluss_t01.csv` | 1 Z-Bon, nötig für die Schema-Inferenz |
| `batch_t02_unsauber` | `kasse/pos_t02.jsonl` | T02-0001 neues Feld `kanal`, T02-0002 `markt_id = "Kiel"`, T02-0003 `Bon_Summe`, T02-0004 abgeschnitten |

## Ablauf (nur in der Umgebung test)

    databricks bundle deploy --target test --profile redbricks
    uv run redbricks-liefern --target test tests/daten/schema/batch_t01_normal
    databricks bundle run verkauf --target test --profile redbricks
    uv run redbricks-liefern --target test tests/daten/schema/batch_t02_unsauber
    databricks bundle run verkauf --target test --profile redbricks

Der zweite Lauf wird wegen der Schemaänderung abgebrochen und startet automatisch neu.

## Erwartetes Ergebnis

    SELECT event_id, markt_id, bon_summe, kanal, _rescued_data
    FROM redbricks_test.test_dp_verkauf.bronze_bons ORDER BY event_id

- 6 Zeilen
- T02-0001: `kanal = SB-KASSE`
- T02-0002: `markt_id = Kiel`
- T02-0003: `bon_summe` leer, `_rescued_data` enthält `Bon_Summe`
- eine Zeile mit `event_id IS NULL` aus `pos_t02.jsonl`