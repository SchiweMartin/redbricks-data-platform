"""Silver Verkauf: Bons und Positionen nach den Fachregeln aus aufgabe.html.

Materialized Views, weil Storno (reihenfolgeunabhängig) und Deduplizierung
(auch gegen Replays nach Tagen) den Gesamtbestand brauchen (ADR 0011).
"""

from pyspark import pipelines as dp
from pyspark.sql import Column, DataFrame, SparkSession, Window
from pyspark.sql import functions as F

from redbricks.verkauf.regeln import (
    BETRAG,
    POSITIONEN_SCHEMA,
    geschaeftstag,
    nettobetrag,
    positionsbetrag,
)

spark = SparkSession.active()

EVENT_TYPEN = ["VERKAUF", "STORNO", "RUECKGABE"]
BON_TYPEN = ["VERKAUF", "RUECKGABE"]


def _try_cast(spalte: str, typ: str) -> Column:
    """Cast, der bei ungültigen Werten NULL liefert statt abzubrechen."""
    return F.expr(f"try_cast({spalte} AS {typ})")


def _ist_storniert() -> Column:
    """Ein Verkaufsbon ist storniert, wenn es zu seiner bon_id ein Storno gibt."""
    return (F.col("event_typ") == "VERKAUF") & F.col("storniert_am").isNotNull()


@dp.temporary_view(name="bon_events")
def bon_events() -> DataFrame:
    """1 Zeile je event_id (erste Ankunft gewinnt), typisiert, mit Gültigkeitskennzeichen."""
    erste_ankunft = Window.partitionBy("event_id").orderBy("_geladen_am", "_quelle_datei")
    events = (
        spark.read.table("bronze_bons")
        .withColumn("_ankunft_nr", F.row_number().over(erste_ankunft))
        .filter((F.col("_ankunft_nr") == 1) | F.col("event_id").isNull())
        .select(
            "event_id",
            "event_typ",
            "bon_id",
            _try_cast("markt_id", "INT").alias("markt_id"),
            _try_cast("kasse_nr", "INT").alias("kasse_nr"),
            _try_cast("bon_zeitpunkt", "TIMESTAMP").alias("bon_zeitpunkt"),
            _try_cast("gesendet_am", "TIMESTAMP").alias("gesendet_am"),
            "kundenkarte_nr",
            "zahlart",
            _try_cast("bon_summe", "DECIMAL(12,2)").alias("bon_summe_kasse"),
            "referenz_bon_id",
            F.from_json("positionen", POSITIONEN_SCHEMA).alias("positionen"),
            "_quelle_datei",
            "_geladen_am",
        )
    )
    ist_bon = F.col("event_typ").isin(BON_TYPEN)
    positionen_ok = (F.size("positionen") > 0) & F.forall("positionen", lambda p: p["menge"] > 0)
    ist_gueltig = (
        F.col("event_id").isNotNull()
        & F.col("event_typ").isin(EVENT_TYPEN)
        & F.col("bon_id").isNotNull()
        & F.col("bon_zeitpunkt").isNotNull()
        & (~ist_bon | (F.col("markt_id").isNotNull() & positionen_ok))
    )
    return events.withColumn("ist_gueltig", F.coalesce(ist_gueltig, F.lit(False))).withColumn(
        "geschaeftstag", geschaeftstag(F.col("bon_zeitpunkt"))
    )


@dp.temporary_view(name="stornierte_bons")
def stornierte_bons() -> DataFrame:
    """Je stornierter bon_id der früheste Storno-Zeitpunkt."""
    return (
        spark.read.table("bon_events")
        .filter(F.col("ist_gueltig") & (F.col("event_typ") == "STORNO"))
        .groupBy("bon_id")
        .agg(F.min("bon_zeitpunkt").alias("storniert_am"))
    )


@dp.materialized_view(
    name="silver_bon_positionen",
    comment="Positionen gültiger Verkaufs- und Rückgabebons mit Brutto/Netto nach Fachregel",
)
def silver_bon_positionen() -> DataFrame:
    bons = spark.read.table("bon_events").filter(
        F.col("ist_gueltig") & F.col("event_typ").isin(BON_TYPEN)
    )
    return (
        bons.join(spark.read.table("stornierte_bons"), "bon_id", "left")
        .select(
            "event_id",
            "bon_id",
            "event_typ",
            "geschaeftstag",
            "bon_zeitpunkt",
            "markt_id",
            "kasse_nr",
            "kundenkarte_nr",
            "referenz_bon_id",
            _ist_storniert().alias("ist_storniert"),
            F.inline("positionen"),
        )
        .withColumn(
            "betrag_brutto", positionsbetrag(F.col("menge"), F.col("einzelpreis"), F.col("rabatt"))
        )
        .withColumn("betrag_netto", nettobetrag(F.col("betrag_brutto"), F.col("steuer_kz")))
    )


@dp.materialized_view(
    name="silver_bons",
    comment="Gültige Verkaufs- und Rückgabebons, 1 Zeile je Bon, Beträge aus den Positionen",
)
def silver_bons() -> DataFrame:
    bons = spark.read.table("bon_events").filter(
        F.col("ist_gueltig") & F.col("event_typ").isin(BON_TYPEN)
    )
    summen = (
        spark.read.table("silver_bon_positionen")
        .groupBy("event_id")
        .agg(
            F.count("*").alias("anzahl_positionen"),
            F.sum("betrag_brutto").cast(BETRAG).alias("betrag_brutto"),
            F.sum("betrag_netto").cast(BETRAG).alias("betrag_netto"),
        )
    )
    return (
        bons.join(spark.read.table("stornierte_bons"), "bon_id", "left")
        .join(summen, "event_id", "left")
        .select(
            "bon_id",
            "event_id",
            "event_typ",
            "geschaeftstag",
            "bon_zeitpunkt",
            "gesendet_am",
            "markt_id",
            "kasse_nr",
            "kundenkarte_nr",
            "zahlart",
            "referenz_bon_id",
            _ist_storniert().alias("ist_storniert"),
            F.when(F.col("event_typ") == "VERKAUF", F.col("storniert_am")).alias("storniert_am"),
            "anzahl_positionen",
            "betrag_brutto",
            "betrag_netto",
            "bon_summe_kasse",
            "_quelle_datei",
            "_geladen_am",
        )
    )
