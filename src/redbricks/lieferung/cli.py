"""Kommandozeile: redbricks-liefern --target dev <batch-ordner>."""

import argparse
from pathlib import Path

from databricks.sdk import WorkspaceClient

from redbricks.lieferung.bundle import lade_bundle_konfiguration, ziel_aus_bundle
from redbricks.lieferung.liefern import liefere_batch


def main() -> None:
    parser = argparse.ArgumentParser(description="Liefert einen Batch in die Landing Zone.")
    parser.add_argument("batch_ordner", type=Path, help="lokaler Batch-Ordner")
    parser.add_argument("--target", required=True, choices=["dev", "test", "prod"])
    parser.add_argument("--profile", default="redbricks", help="Databricks-CLI-Profil")
    args = parser.parse_args()

    if not args.batch_ordner.is_dir():
        parser.error(f"Ordner nicht gefunden: {args.batch_ordner}")

    ziel = ziel_aus_bundle(lade_bundle_konfiguration(args.target, args.profile))
    print(f"Ziel: {ziel.volume_pfad}")
    client = WorkspaceClient(profile=args.profile)
    anzahl = liefere_batch(client, ziel, args.batch_ordner)
    print(f"Fertig: {anzahl} Dateien geliefert.")
