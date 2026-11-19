"""Bronze: Kassen Events roh aus der Landing Zone, Append-only."""

from pyspark import pipelines as dp
from pyspark.sql import SparkSession

from redbricks.bronze import mit_herkunft

spark = SparkSession.active()
LANDING = spark.conf.get("redbricks.landing_pfad")


@dp.table(
    name="bronze_bons",
    comment="Kassen-Events (Verkauf, Storno, Rückgabe) roh aus pos_*.jsonl, mit Herkunft",
)
def bronze_bons():
    return mit_herkunft(
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("pathGlobFilter", "pos_*.jsonl")
        .load(f"{LANDING}/kasse")
    )
