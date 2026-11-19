"""Bronze: Kassenabschluesse roh aus der Landing Zone, Append-only."""

from pyspark import pipelines as dp
from pyspark.sql import SparkSession

from redbricks.bronze import mit_herkunft

spark = SparkSession.active()
LANDING = spark.conf.get("redbricks.landing_pfad")


@dp.table(
    name="bronze_kassenabschluesse",
    comment="Tagesabschlüsse der Kassen (Z-Bon) roh aus kassenabschluss_*.csv, mit Herkunft",
)
def bronze_kassenabschluesse():
    return mit_herkunft(
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .option("pathGlobFilter", "kassenabschluss_*.csv")
        .load(f"{LANDING}/kasse")
    )
