"""Lieferplan: welche lokalen Dateien wohin im Volume geliefert werden."""

import hashlib
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Datei:
    """Eine zu liefernde Datei."""

    batch: str
    quelle: str
    name: str
    lokaler_pfad: Path
    zielpfad: str
    groesse_bytes: int
    sha256: str


def pruefsumme(pfad: Path) -> str:
    """Berechnet die SHA-256-Prüfsumme einer Datei."""
    return hashlib.sha256(pfad.read_bytes()).hexdigest()


def plane_lieferung(batch_ordner: Path, volume_pfad: str) -> list[Datei]:
    """Erstellt den Lieferplan für einen Batch-Ordner.

    Erwartete Struktur: <batch_ordner>/<quelle>/<datei>.
    Ziel im Volume: <volume_pfad>/<quelle>/<batch>/<datei>.
    Versteckte Dateien und Ordner (z. B. .DS_Store) werden ignoriert.
    """
    batch = batch_ordner.name
    dateien = []
    for quell_ordner in sorted(batch_ordner.iterdir()):
        if not quell_ordner.is_dir() or quell_ordner.name.startswith("."):
            continue
        quelle = quell_ordner.name
        for pfad in sorted(quell_ordner.iterdir()):
            if not pfad.is_file() or pfad.name.startswith("."):
                continue
            dateien.append(
                Datei(
                    batch=batch,
                    quelle=quelle,
                    name=pfad.name,
                    lokaler_pfad=pfad,
                    zielpfad=f"{volume_pfad}/{quelle}/{batch}/{pfad.name}",
                    groesse_bytes=pfad.stat().st_size,
                    sha256=pruefsumme(pfad),
                )
            )
    return dateien
