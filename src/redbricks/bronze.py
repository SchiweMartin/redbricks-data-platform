"""Gemeinsame Bausteine für Bronze-Tabellen aller Data Products."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def mit_herkunft(df: DataFrame) -> DataFrame:
    """Hängt Herkunftsspalten an: Quelldatei, Änderungszeit der Datei, Ladezeitpunkt.

    Erwartet einen DataFrame aus Auto Loader, damit die Spalte _metadata verfügbar ist.
    """

    return df.select(
        "*",
        F.col("_metadata.file_path").alias("_quelle_datei"),
        F.col("_metadata.file_modification_time").alias("_datei_geaendert_am"),
        F.current_timestamp().alias("_geladen_am"),
    )
