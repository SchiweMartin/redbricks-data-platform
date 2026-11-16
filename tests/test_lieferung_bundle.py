import pytest

from redbricks.lieferung.bundle import Ziel, ziel_aus_bundle

BEISPIEL = {
    "variables": {
        "catalog": {"value": "redbricks_dev"},
        "warehouse_id": {"value": "abc123"},
    },
    "resources": {
        "schemas": {"betrieb": {"name": "dev_x_betrieb"}},
        "volumes": {"batches": {"volume_path": "/Volumes/redbricks_dev/dev_x_eingang/batches"}},
    },
}


def test_ziel_aus_bundle_liest_alle_werte():
    assert ziel_aus_bundle(BEISPIEL) == Ziel(
        catalog="redbricks_dev",
        schema_betrieb="dev_x_betrieb",
        volume_pfad="/Volumes/redbricks_dev/dev_x_eingang/batches",
        warehouse_id="abc123",
    )


def test_ziel_aus_bundle_ohne_warehouse_schlaegt_fehl():
    ohne_warehouse = {**BEISPIEL, "variables": {"catalog": {"value": "redbricks_dev"}}}
    with pytest.raises(KeyError):
        ziel_aus_bundle(ohne_warehouse)
