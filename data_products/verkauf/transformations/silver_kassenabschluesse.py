"""Silver Verkauf: Tagesabschlüsse (Z-Bons), 1 Zeile je Geschäftstag, Markt und Kasse.

Der Z-Bon ist die fachliche Referenz der Kasse und dient als Vollständigkeitsprüfung
für die Bons (kennt auch Bons, die die Zentrale noch nicht erreicht haben).
"""

from pyspark import pipelines as dp
from pyspark.sql import Column, DataFrame, SparkSession, Window
from pyspark.sql import functions as F

spark = SparkSession.active()

SCHLUESSEL = ["geschaeftstag", "markt_id", "kasse_nr"]


def _try_cast(spalte: str, typ: str) -> Column:
    """Cast, der bei ungültigen Werten NULL liefert statt abzubrechen."""
    return F.expr(f"try_cast({spalte} AS {typ})")


@dp.materialized_view(
    name="silver_kassenabschluesse",
    comment="Z-Bons typisiert, 1 Zeile je Geschäftstag, Markt und Kasse (letzter Stand gewinnt)",
)
def silver_kassenabschluesse() -> DataFrame:
    typisiert = spark.read.table("bronze_kassenabschluesse").select(
        _try_cast("geschaeftstag", "DATE").alias("geschaeftstag"),
        _try_cast("markt_id", "INT").alias("markt_id"),
        _try_cast("kasse_nr", "INT").alias("kasse_nr"),
        _try_cast("anzahl_verkaufsbons", "INT").alias("anzahl_verkaufsbons"),
        _try_cast("umsatz_brutto", "DECIMAL(12,2)").alias("umsatz_brutto"),
        _try_cast("storno_summe", "DECIMAL(12,2)").alias("storno_summe"),
        _try_cast("rueckgabe_summe", "DECIMAL(12,2)").alias("rueckgabe_summe"),
        _try_cast("erstellt_am", "TIMESTAMP").alias("erstellt_am"),
        "_quelle_datei",
        "_geladen_am",
    )
    letzter_stand = Window.partitionBy(*SCHLUESSEL).orderBy(
        F.col("erstellt_am").desc_nulls_last(), F.col("_geladen_am").desc()
    )
    schluessel_vollstaendig = F.col("geschaeftstag").isNotNull()
    for spalte in SCHLUESSEL[1:]:
        schluessel_vollstaendig = schluessel_vollstaendig & F.col(spalte).isNotNull()
    return (
        typisiert.filter(schluessel_vollstaendig)
        .withColumn("_stand_nr", F.row_number().over(letzter_stand))
        .filter(F.col("_stand_nr") == 1)
        .drop("_stand_nr")
    )
