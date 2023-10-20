import pandas as pd
import numpy as np
import re


def extractCounts(
    series: pd.Series,
    counts: str,
) -> pd.Series:
    rx = r"(\d+)\s*?" + counts

    countsValues = series.str.findall(rx, flags=re.IGNORECASE)
    countsValues = countsValues.apply(
        lambda _counts: [count for count in _counts if str(count) != "1"]
    )
    return countsValues


def excractNoCounts(
    series: pd.Series,
    counts: str,
) -> pd.Series:
    rx = counts + r"\s*?(\d+)"

    countsValues = series.str.findall(rx, flags=re.IGNORECASE)
    countsValues = countsValues.apply(
        lambda _counts: [count for count in _counts if count != "1"]
    )
    return countsValues


def createCountsRX(
    countsValues: pd.Series,
    counts: str,
) -> pd.Series:
    countsRX = countsValues.str[:1].str.join("").astype(str)
    countsRX = countsRX.where(
        countsRX == "", r"(?=.*(\D" + countsRX + r"\s*" + counts + "))"
    )

    return countsRX


def createNoCountsRX(
    countsValues: pd.Series,
    default_counts: str,
    No_counts: str,
) -> pd.Series:
    countsRX = countsValues.str[:1].str.join("").astype(str)
    countsRX = countsRX.where(
        countsRX == "",
        r"(?=.*(\D"
        + countsRX
        + r"\s*"
        + default_counts
        + "|"
        + No_counts
        + r"\s*"
        + countsRX
        + r"\D))",
    )

    return countsRX


def createExcludeCountsRX(
    countsValues: pd.Series,
    counts: str,
) -> pd.Series:
    def fullmatch(cell):
        if re.fullmatch(r"\d+", cell):
            return False
        return True

    countsRX = countsValues.str[:1].str.join("").astype(str)
    countsRX = countsRX.where(
        countsRX != "",
        r"(?!.*((?:[0-9][0-9]\d*|[2-9]\d*?)\s*" + counts + "))",
    )

    countsRX = countsRX.where(countsRX.apply(fullmatch), "")
    return countsRX


def createExcludeNoCountsRX(
    countsValues: pd.Series,
    default_counts: str,
    No_counts: str,
) -> pd.Series:
    def fullmatch(cell):
        if re.fullmatch(r"\d+", cell):
            return False
        return True

    countsRX = countsValues.str[:1].str.join("").astype(str)
    countsRX = countsRX.where(
        countsRX != "",
        r"(?!.*((?:[0-9][0-9]\d*|[2-9]\d*)\s*"
        + default_counts
        + "|"
        + No_counts
        + r"(?:[0-9][0-9]\d*|[2-9]\d*)"
        + "))",
    )

    countsRX = countsRX.where(countsRX.apply(fullmatch), "")
    return countsRX
