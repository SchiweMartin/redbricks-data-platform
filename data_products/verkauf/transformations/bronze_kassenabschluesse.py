"""Bronze: Kassenabschluesse roh aus der Landing Zone, Append-only."""

from pyspark import pipelines as dp
from pyspark.sql import SparkSession
from pyspark.sql import functions as F

spark = SparkSession.active()
LANDING = spark.conf.get("redbricks.landing_pfad")


@dp.table(
    name="bronze_kassenabschluesse",
    comment="Tagesabschlüsse der Kassen (Z-Bon) roh aus kassenabschluss_*.csv, mit Herkunft",
)
def bronze_kassenabschluesse():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("pathGlobFilter", "kassenabschluss_*.csv")
        .load(f"{LANDING}/kasse")
        .select(
            "*",
            F.col("_metadata.file_path").alias("_quelle_datei"),
            F.col("_metadata.file_modification_time").alias("_datei_geaendert_am"),
            F.current_timestamp().alias("_geladen_am"),
        )
    )
