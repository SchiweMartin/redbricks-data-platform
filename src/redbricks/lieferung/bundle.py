"""Ziel der Lieferung aus der aufgelösten Bundle-Konfiguration ermitteln."""

import json
import subprocess
from dataclasses import dataclass


@dataclass(frozen=True)
class Ziel:
    """Wohin geliefert und wo protokolliert wird."""

    catalog: str
    schema_betrieb: str
    volume_pfad: str
    warehouse_id: str


def ziel_aus_bundle(konfiguration: dict) -> Ziel:
    """Liest die benötigten Werte aus der Ausgabe von `bundle validate --output json`."""
    variablen = konfiguration["variables"]
    ressourcen = konfiguration["resources"]
    return Ziel(
        catalog=variablen["catalog"]["value"],
        schema_betrieb=ressourcen["schemas"]["betrieb"]["name"],
        volume_pfad=ressourcen["volumes"]["batches"]["volume_path"],
        warehouse_id=variablen["warehouse_id"]["value"],
    )


def lade_bundle_konfiguration(target: str, profil: str) -> dict:
    """Ruft die Databricks CLI auf und gibt die aufgelöste Bundle-Konfiguration zurück."""
    befehl = [
        "databricks",
        "bundle",
        "validate",
        "--target",
        target,
        "--profile",
        profil,
        "--output",
        "json",
    ]
    ergebnis = subprocess.run(befehl, capture_output=True, text=True, check=True)
    return json.loads(ergebnis.stdout)
