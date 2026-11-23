# ADR 0010: Orchestrierung über Lakeflow Job mit File-Arrival-Trigger

- Status: akzeptiert
- Datum: 2026-11-20
- Ticket: RB-205

## Kontext

Batches werden von `redbricks-liefern` in das Volume `eingang.batches` geschrieben.
Die Verarbeitung soll ohne manuellen Start beginnen, sobald eine Lieferung vollständig
angekommen ist. Eine Lieferung besteht aus mehreren Dateien, die nacheinander geschrieben
werden. Ein Start nach der ersten Datei würde einen Teil-Batch verarbeiten.

Die Free Edition erlaubt nur Serverless-Compute, eine aktive Pipeline pro Typ und
höchstens 5 parallele Tasks.

## Entscheidung

- Ein Lakeflow Job `verarbeitung` orchestriert die Pipelines der Data Products.
  Jede Pipeline ist ein `pipeline_task`, aktuell nur `verkauf`.
- Auslöser ist ein **File-Arrival-Trigger** auf das Volume `eingang.batches`:
  - `wait_after_last_change_seconds: 120`: Start erst, wenn 2 Minuten keine neue Datei kam.
    So wird eine Lieferung als Ganzes verarbeitet.
  - `min_time_between_triggers_seconds: 120`: kein Dauerfeuer bei vielen Lieferungen.
- `max_concurrent_runs: 1` mit `queue.enabled: true`: Läufe überholen sich nie.
  Eine Lieferung während eines Laufs wird eingereiht, nicht verworfen.
- Task-Retries: `max_retries: 2`, `min_retry_interval_millis: 120000`. Fängt
  vorübergehende Fehler ab, auch den automatischen Neustart nach Schemaänderung (ADR 0009).
- `full_refresh: false`: Auto Loader verarbeitet dank Checkpoint nur neue Dateien,
  ein Lauf ist idempotent.
- Pausierung je Umgebung:
  - dev: Trigger explizit `UNPAUSED`. Der Development-Mode pausiert sonst alle Trigger,
    und das Preset `trigger_pause_status` kann nicht `UNPAUSED` setzen.
  - test: `PAUSED` per Preset, Läufe werden gezielt gestartet.
  - prod: aktiv.

## Konsequenzen

- Lieferung und Verarbeitung sind entkoppelt. Der Lieferant braucht keine Rechte auf
  Jobs oder Pipelines.
- Zwischen Lieferung und Ergebnis liegen einige Minuten (Wartezeit + Polling des Triggers
  + Start der Serverless-Pipeline). Nachgewiesen mit Batch 001: Lieferung 12:57 UTC,
  Job-Start ca. 13:02 UTC, Bronze aktuell 13:05 UTC (725 Zeilen, Summe 41.377 = Inventar).
- Neue Data Products werden als weitere Tasks im selben Job ergänzt.
  Abhängigkeiten werden über `depends_on` modelliert.
- Der Trigger überwacht nur einen Pfad. Alle Quellen müssen unter `eingang.batches`
  geliefert werden.