"""Lieferprotokoll: Delta-Tabelle im Schema betrieb, eine Zeile je gelieferter Datei."""

import time

from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementParameterListItem, StatementState

from redbricks.lieferung.bundle import Ziel
from redbricks.lieferung.plan import Datei


def tabellenname(ziel: Ziel) -> str:
    """Vollständiger Name der Protokolltabelle."""
    return f"`{ziel.catalog}`.`{ziel.schema_betrieb}`.lieferprotokoll"


def fuehre_sql_aus(
    client: WorkspaceClient,
    ziel: Ziel,
    sql: str,
    parameter: list[StatementParameterListItem] | None = None,
) -> list[list[str]]:
    """Führt eine SQL-Anweisung im Warehouse aus und gibt die Ergebniszeilen zurück."""
    antwort = client.statement_execution.execute_statement(
        warehouse_id=ziel.warehouse_id,
        statement=sql,
        parameters=parameter,
        wait_timeout="50s",
    )
    while antwort.status.state in (StatementState.PENDING, StatementState.RUNNING):
        time.sleep(2)
        antwort = client.statement_execution.get_statement(antwort.statement_id)
    if antwort.status.state != StatementState.SUCCEEDED:
        fehler = antwort.status.error.message if antwort.status.error else antwort.status.state
        raise RuntimeError(f"SQL fehlgeschlagen: {fehler}")
    if antwort.result and antwort.result.data_array:
        return antwort.result.data_array
    return []


def erstelle_tabelle(client: WorkspaceClient, ziel: Ziel) -> None:
    """Legt die Protokolltabelle an, falls sie noch nicht existiert."""
    sql = f"""
        CREATE TABLE IF NOT EXISTS {tabellenname(ziel)} (
            batch STRING NOT NULL COMMENT 'Name des Batch-Ordners, z. B. batch_001_events',
            quelle STRING NOT NULL COMMENT 'Quellsystem, z. B. kasse',
            datei STRING NOT NULL COMMENT 'Dateiname',
            zielpfad STRING NOT NULL COMMENT 'Pfad im Volume, eindeutig je gelieferter Datei',
            groesse_bytes BIGINT COMMENT 'Dateigröße in Bytes',
            sha256 STRING COMMENT 'SHA-256-Prüfsumme des Dateiinhalts',
            geliefert_am TIMESTAMP NOT NULL COMMENT 'Zeitpunkt der Lieferung (UTC)',
            geliefert_von STRING COMMENT 'Benutzer, der geliefert hat'
        )
        COMMENT 'Protokoll aller Lieferungen in die Landing Zone, eine Zeile je Datei'
    """
    fuehre_sql_aus(client, ziel, sql)


def bereits_geliefert(client: WorkspaceClient, ziel: Ziel, batch: str) -> set[str]:
    """Gibt die Zielpfade zurück, die für diesen Batch schon protokolliert sind."""
    sql = f"SELECT zielpfad FROM {tabellenname(ziel)} WHERE batch = :batch"
    zeilen = fuehre_sql_aus(
        client, ziel, sql, [StatementParameterListItem(name="batch", value=batch)]
    )
    return {zeile[0] for zeile in zeilen}


def protokolliere(client: WorkspaceClient, ziel: Ziel, datei: Datei, benutzer: str) -> None:
    """Schreibt eine Zeile für eine gelieferte Datei ins Protokoll."""
    sql = f"""
        INSERT INTO {tabellenname(ziel)}
        VALUES (:batch, :quelle, :datei, :zielpfad, :groesse_bytes, :sha256,
                current_timestamp(), :benutzer)
    """
    parameter = [
        StatementParameterListItem(name="batch", value=datei.batch),
        StatementParameterListItem(name="quelle", value=datei.quelle),
        StatementParameterListItem(name="datei", value=datei.name),
        StatementParameterListItem(name="zielpfad", value=datei.zielpfad),
        StatementParameterListItem(
            name="groesse_bytes", value=str(datei.groesse_bytes), type="BIGINT"
        ),
        StatementParameterListItem(name="sha256", value=datei.sha256),
        StatementParameterListItem(name="benutzer", value=benutzer),
    ]
    fuehre_sql_aus(client, ziel, sql, parameter)
