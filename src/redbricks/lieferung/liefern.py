"""Einen Batch in die Landing Zone liefern."""

from pathlib import Path

from databricks.sdk import WorkspaceClient

from redbricks.lieferung.bundle import Ziel
from redbricks.lieferung.plan import Datei, plane_lieferung
from redbricks.lieferung.protokoll import bereits_geliefert, erstelle_tabelle, protokolliere


def offene_dateien(plan: list[Datei], geliefert: set[str]) -> list[Datei]:
    """Dateien aus dem Plan, die laut Protokoll noch nicht geliefert sind."""
    return [datei for datei in plan if datei.zielpfad not in geliefert]


def liefere_batch(client: WorkspaceClient, ziel: Ziel, batch_ordner: Path) -> int:
    """Liefert alle offenen Dateien eines Batches und gibt deren Anzahl zurück."""
    plan = plane_lieferung(batch_ordner, ziel.volume_pfad)
    if not plan:
        raise ValueError(f"Keine Dateien in {batch_ordner} gefunden.")

    erstelle_tabelle(client, ziel)
    geliefert = bereits_geliefert(client, ziel, batch_ordner.name)
    offen = offene_dateien(plan, geliefert)

    print(f"Batch {batch_ordner.name}: {len(plan)} Dateien, davon {len(offen)} offen.")
    if not offen:
        print("Nichts zu tun: Der Batch wurde bereits vollständig geliefert.")
        return 0

    benutzer = client.current_user.me().user_name
    for nummer, datei in enumerate(offen, start=1):
        with datei.lokaler_pfad.open("rb") as inhalt:
            client.files.upload(datei.zielpfad, inhalt, overwrite=False)
        protokolliere(client, ziel, datei, benutzer)
        print(f"  [{nummer}/{len(offen)}] {datei.quelle}/{datei.name}")
    return len(offen)
