"""Fachregeln Verkauf aus aufgabe.html, an genau einer Stelle umgesetzt.

Pipeline und Tests nutzen ausschließlich diese Funktionen.
"""

from decimal import Decimal

from pyspark.sql import Column
from pyspark.sql import functions as F
from pyspark.sql.types import (
    ArrayType,
    DecimalType,
    IntegerType,
    StringType,
    StructField,
    StructType,
)

ZEITZONE = "Europe/Berlin"

BETRAG = DecimalType(12, 2)

MWST_SAETZE = {
    "A": Decimal("0.19"),
    "B": Decimal("0.07"),
}

POSITIONEN_SCHEMA = ArrayType(
    StructType(
        [
            StructField("pos_nr", IntegerType()),
            StructField("artikel_nr", IntegerType()),
            StructField("menge", IntegerType()),
            StructField("einzelpreis", BETRAG),
            StructField("rabatt", BETRAG),
            StructField("steuer_kz", StringType()),
        ]
    )
)


def geschaeftstag(zeitpunkt_utc: Column) -> Column:
    """Geschäftstag: Datum des Vorgangs in Ortszeit (Europe/Berlin)."""
    return F.to_date(F.from_utc_timestamp(zeitpunkt_utc, ZEITZONE))


def mwst_satz(steuer_kz: Column) -> Column:
    """MwSt-Satz zum Steuerkennzeichen. Unbekanntes Kennzeichen ergibt NULL."""
    satz = F.when(F.lit(False), F.lit(None))
    for kz, wert in MWST_SAETZE.items():
        satz = satz.when(steuer_kz == kz, F.lit(wert))
    return satz


def positionsbetrag(menge: Column, einzelpreis: Column, rabatt: Column) -> Column:
    """Positionsbetrag = Menge x Einzelpreis - Rabatt, auf Cent gerundet (inkl. MwSt)."""
    return F.round(menge * einzelpreis - rabatt, 2).cast(BETRAG)


def nettobetrag(betrag: Column, steuer_kz: Column) -> Column:
    """Nettobetrag = Positionsbetrag / (1 + MwSt-Satz), auf Cent gerundet."""
    return F.round(betrag / (F.lit(Decimal("1")) + mwst_satz(steuer_kz)), 2).cast(BETRAG)
