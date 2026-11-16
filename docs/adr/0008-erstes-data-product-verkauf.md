# ADR 0008: Erstes Data Product ist Verkauf

- **Status:** Akzeptiert
- **Datum:** 2026-11-16
- **Ticket:** RB-202

## Kontext

Laut Lernpfad wird zuerst ein Data Product vollständig gebaut, von der Rohdatei bis Silver,
mit Qualität, Contract, Tests und CI/CD. Aus ihm wird anschließend der Blueprint für alle
weiteren Data Products abgeleitet (RB-501). Zur Wahl stehen die vier Data Products aus
ADR 0007.

## Entscheidung

Das erste Data Product ist **Verkauf** (`dp_verkauf`, Quellen: Kasse-Bons und Z-Bon,
Lademuster Append-only).

### Was daran gelernt wird

- Auto Loader und Streaming Tables für Append-only, das häufigste Lademuster
- Dubletten, verspätete Daten und falsche Reihenfolge (Storno vor Verkauf):
  Deduplizierung und Watermarks
- Schema-Evolution und Rescued Data (neue Felder der Kassensoftware)
- Datenqualität und Quarantäne (technisch kaputte Events, fehlerhafte Lieferungen)
- Fachregeln im Paket `redbricks` mit Unit Tests (Geschäftstag, Beträge, Storno, Rückgabe)
- Abgleich zweier Quellen (Bons gegen Z-Bon) als Qualitätsprüfung
- Direkte Kontrolle über sieben Abstimmwerte des Controllings nach jedem Batch

### Risiko und Gegenmaßnahmen

| Risiko | Gegenmaßnahme |
|---|---|
| Viele Fachregeln auf einmal, Gefahr, sich zu verzetteln | Schrittweise bauen: erst Bronze vollständig, dann Silver Regel für Regel, jede mit Test |
| Größte Datenmenge, höchster Verbrauch des Free-Edition-Kontingents | Pipelines getriggert statt kontinuierlich; in der Entwicklung mit wenigen Dateien arbeiten |
| CDC und Full Load kommen im ersten Data Product nicht vor | Blueprint in RB-501 beim Bau von Kunde und Stammdaten um diese Lademuster erweitern |

## Betrachtete Alternativen

### Option A: Verkauf (gewählt)
Begründung siehe oben.

### Option B: Stammdaten (verworfen)
- Vorteile:
  - Kleinste Datenmenge, wenige Regeln, leichter Einstieg
- Nachteile:
  - Kaum direkt prüfbare Abstimmwerte
  - Wenig Prüfungsthemen aus Modul 2 und 3 (kein Auto Loader, keine Dubletten, keine Watermarks)
- Grund für die Ablehnung: Als Vorlage für Bewegungsdaten zu wenig aussagekräftig.

### Option C: Kunde (verworfen)
- Vorteile:
  - CDC, SCD 1 und 2, DSGVO: viel Prüfungsstoff
- Nachteile:
  - Hohe Komplexität bei wenigen direkt prüfbaren Abstimmwerten
- Grund für die Ablehnung: Zu riskant als erstes Data Product ohne schnelles Feedback.

### Option D: Warenfluss (verworfen)
- Grund für die Ablehnung: Hängt von Verkauf und Stammdaten ab, die noch nicht existieren.

## Konsequenzen

- Positiv: Schnelles, messbares Feedback über die Abstimmwerte; der Blueprint deckt das
  häufigste Lademuster ab.
- Negativ: Der Blueprint muss später um CDC und Full Load erweitert werden.
- Folgemaßnahmen: RB-203 lädt Bons und Z-Bons per Auto Loader nach Bronze.