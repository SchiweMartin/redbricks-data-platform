from pathlib import Path

from redbricks.lieferung.liefern import offene_dateien
from redbricks.lieferung.plan import Datei


def datei(name: str) -> Datei:
    return Datei(
        batch="batch_001_events",
        quelle="kasse",
        name=name,
        lokaler_pfad=Path(name),
        zielpfad=f"/Volumes/c/s/batches/kasse/batch_001_events/{name}",
        groesse_bytes=1,
        sha256="x",
    )


def test_bereits_gelieferte_dateien_werden_uebersprungen():
    plan = [datei("a.jsonl"), datei("b.jsonl")]
    geliefert = {"/Volumes/c/s/batches/kasse/batch_001_events/a.jsonl"}

    assert [d.name for d in offene_dateien(plan, geliefert)] == ["b.jsonl"]


def test_alles_geliefert_ergibt_leere_liste():
    plan = [datei("a.jsonl")]
    geliefert = {plan[0].zielpfad}

    assert offene_dateien(plan, geliefert) == []
