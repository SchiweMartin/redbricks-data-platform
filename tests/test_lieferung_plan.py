from pathlib import Path

from redbricks.lieferung.plan import plane_lieferung

VOLUME = "/Volumes/c/s/batches"


def lege_an(pfad: Path, inhalt: str = "x") -> None:
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text(inhalt)


def test_zielpfad_je_quelle_und_batch(tmp_path):
    batch = tmp_path / "batch_001_events"
    lege_an(batch / "kasse" / "pos_1.jsonl")

    plan = plane_lieferung(batch, VOLUME)

    assert len(plan) == 1
    assert plan[0].quelle == "kasse"
    assert plan[0].batch == "batch_001_events"
    assert plan[0].zielpfad == "/Volumes/c/s/batches/kasse/batch_001_events/pos_1.jsonl"


def test_versteckte_dateien_werden_ignoriert(tmp_path):
    batch = tmp_path / "batch_000_initial"
    lege_an(batch / ".DS_Store")
    lege_an(batch / "kasse" / ".DS_Store")
    lege_an(batch / "kasse" / "pos_1.jsonl")

    plan = plane_lieferung(batch, VOLUME)

    assert [d.name for d in plan] == ["pos_1.jsonl"]


def test_gleicher_inhalt_wird_trotzdem_geliefert(tmp_path):
    batch = tmp_path / "batch_005_late_replay"
    lege_an(batch / "kasse" / "a.jsonl", "gleicher Inhalt")
    lege_an(batch / "kasse" / "b.jsonl", "gleicher Inhalt")

    a, b = plane_lieferung(batch, VOLUME)

    assert a.sha256 == b.sha256
    assert a.zielpfad != b.zielpfad
