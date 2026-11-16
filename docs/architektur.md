# Zielarchitektur redbricks Data Platform

Übersicht über Quellen, Data Products und Use Cases. Entscheidungen: ADR 0004, 0006, 0007.

```mermaid
flowchart LR
    subgraph Q[Quellsysteme]
        K[Kasse<br/>Bons, Z-Bon]
        C[CRM]
        W[Lagerverwaltung]
        B[Bestandsmeldung]
        WW[Warenwirtschaft<br/>Artikel, Lieferanten,<br/>Märkte, Feiertage]
    end

    L[(Landing Zone<br/>eingang.batches)]
    K & C & W & B & WW -->|redbricks-liefern| L

    subgraph DP[Data Products: Bronze → Silver]
        V[dp_verkauf<br/>Append-only]
        KU[dp_kunde<br/>CDC]
        S[dp_stammdaten<br/>Full Load]
        WF[dp_warenfluss<br/>CDC + Append-only<br/>+ Nachschub]
    end

    L --> V & KU & S & WF
    V & S --> WF

    SL[Semantic Layer<br/>kennzahlen]
    V & KU & S & WF --> SL

    SL --> UC1[Use Case 1<br/>AI/BI-Dashboard<br/>Vertriebsleitung]
    WF --> LB[(Lakebase)]
    LB <--> UC2[Use Case 2<br/>App<br/>Marktleitungen]
    LB -->|Entscheidungen| WF

    BT[betrieb<br/>Lieferprotokoll,<br/>Datenqualität] -.-> UC1
```

## Data Products

| Data Product | Owner | Quellen | Lademuster |
|---|---|---|---|
| `dp_verkauf` | Vertrieb | Kasse: Bons, Z-Bon | Append-only |
| `dp_kunde` | Kundenmanagement | CRM | CDC |
| `dp_stammdaten` | Warenwirtschaft | Artikel, Lieferanten, Märkte, Feiertage | Full Load |
| `dp_warenfluss` | Logistik und Disposition | Lagerverwaltung, Bestand | CDC, Append-only |

## Schichten je Data Product

| Präfix | Schicht | Sichtbarkeit |
|---|---|---|
| `bronze_` | Rohdaten mit Herkunft, unverändert | intern |
| `quarantine_` | fehlerhafte Datensätze mit Grund | intern |
| `silver_` | bereinigt, nach Fachregeln | **veröffentlicht** |
| `gold_` | nutzerorientierte Ergebnisse (Nachschub) | **veröffentlicht** |