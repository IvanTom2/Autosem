from autosem_funcs.counts_extraction_funcs import (
    extractCounts,
    createCountsRX,
    createExcludeCountsRX,
    excractNoCounts,
    createNoCountsRX,
    createExcludeNoCountsRX,
)
from common import Extractor

import warnings
import pandas as pd

warnings.filterwarnings("ignore")


class CountsExtractor(Extractor):
    """
    Extract counts from rows and make regex for them.
    Example: 15 шт -> extract "15"

    - counts - counts feature for extracting through regex.
    - excludeRX - make special regex for rows where counts weren't extracted.
    """

    def __init__(
        self,
        counts: str = "шт|уп|бан|пач",
        excludeRX: bool = False,
    ) -> None:
        self.counts = counts
        self.excludeRX = excludeRX

    def extract(
        self,
        data: pd.DataFrame,
        col: str = "Название",
    ) -> pd.DataFrame:
        """
        return dataframe with two extra columns:
        1) "Количество"
        2) "Исключающее количество"
        """
        counts = "(?:" + counts + ")"
        countsValues = extractCounts(data[col], counts)
        countsDefaultRX = createCountsRX(countsValues, counts)

        countsExcludeRX = pd.Series()
        if self.excludeRX:
            countsExcludeRX = createExcludeCountsRX(countsValues, counts)

        data["Количество"] = countsDefaultRX
        data["Исключающее количество"] = countsExcludeRX

        return data


class CountsNoExtractor(Extractor):
    """
    Extract counts and '№' from rows and make regex for them.
    Example: 15 шт -> extract "15"
    Example: №16 -> extract "16"

    - counts - counts feature for extracting through regex.
    - NO - '№' feature for extracting through regex.
    - excludeRX - make special regex for rows where counts weren't extracted.
    """

    def __init__(
        self,
        counts: str = "шт|уп",
        NO: str = "№|n",
        excludeRX: bool = False,
    ) -> None:
        self.counts = counts
        self.NO = NO
        self.excludeRX = excludeRX

    def extract(
        self,
        data: pd.DataFrame,
        col="Название",
    ) -> pd.DataFrame:
        """
        return dataframe with two extra columns:
        1) "Количество (№)"
        2) "Исключающее количество (№)"
        """

        default_counts = "(?:" + self.counts + ")"
        No_counts = "(?:" + self.NO + ")"

        default_values = extractCounts(data[col], default_counts)
        No_values = excractNoCounts(data[col], No_counts)

        # No_values in 1-st priority
        countsValues = No_values + default_values
        countsDefaultRX = createNoCountsRX(countsValues, default_counts, No_counts)

        countsExcludeRX = pd.Series()
        if self.excludeRX:
            countsExcludeRX = createExcludeNoCountsRX(
                countsValues, default_counts, No_counts
            )

        data["Количество (№)"] = countsDefaultRX
        data["Исключающее количество (№)"] = countsExcludeRX

        return data


if __name__ == "__main__":
    data = pd.DataFrame()
    data.at[0, "Название"] = "Яблоки 19 штук"
    data.at[1, "Название"] = "Яблоки 10 упаковок"
    data.at[2, "Название"] = "Яблоки 5 штук №228"
    data.at[3, "Название"] = "Яблоки 1 штук"
    data.at[4, "Название"] = "Яблоки №3"

    extractor = CountsExtractor(excludeRX=True)
    data = extractor.extract(data, "Название")
    data.to_excel("checkout.xlsx")
