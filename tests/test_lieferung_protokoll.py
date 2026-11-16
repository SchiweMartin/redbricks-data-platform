from redbricks.lieferung.bundle import Ziel
from redbricks.lieferung.protokoll import tabellenname


def test_tabellenname_mit_backticks():
    ziel = Ziel(
        catalog="redbricks_dev",
        schema_betrieb="dev_x_betrieb",
        volume_pfad="/Volumes/redbricks_dev/dev_x_eingang/batches",
        warehouse_id="abc123",
    )
    assert tabellenname(ziel) == "`redbricks_dev`.`dev_x_betrieb`.lieferprotokoll"
