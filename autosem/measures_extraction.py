from autosem_funcs.measures_extraction_funcs import (
    Measures,
    extractMeasureValues,
    createMeasureRX,
)
from counts_extraction import Extractor

import pandas as pd


class MeasuresData(object):
    """
    Contains data for any type of measures:
    - technique
    - concByMilliliter
    - concPercent
    - liquid
    - mass
    - ME
    """

    def __init__(self):
        pass

    @property
    def memory(self):
        _name = "Емкость памяти"
        prefix = ""
        postfix = ""
        measure_data = [
            {
                "name": "Гигабайт",
                "symbols": r"gb|gigabite|гигабайт|гб",
                "ratio": 1,
                "prefix": prefix,
                "postfix": postfix,
            },
        ]
        return _name, measure_data

    @property
    def concByMilliliter(self):
        _name = "Концентрация в миллилитрах"
        prefix = ""
        postfix = ""
        measure_data = [
            {
                "name": "Мкг/мл",
                "symbols": r"мкг.мл",
                "ratio": 0.000001,
                "prefix": prefix,
                "postfix": postfix,
            },
            {
                "name": "Мг/мл",
                "symbols": r"мг.мл",
                "ratio": 0.001,
                "prefix": prefix,
                "postfix": postfix,
            },
            {
                "name": "%содержания",
                "symbols": r"%",
                "ratio": 0.01,
                "prefix": prefix,
                "postfix": postfix,
            },
            {
                "name": "Г/мл",
                "symbols": r"г.мл",
                "ratio": 1,
                "prefix": prefix,
                "postfix": postfix,
            },
        ]
        return _name, measure_data

    @property
    def concPercent(self):
        _name = "Концентрация только в процентах"
        prefix = r""
        postfix = r""
        measure_data = [
            {
                "name": "Процент",
                "symbols": r"%",
                "ratio": 1,
                "prefix": prefix,
                "postfix": postfix,
            },
        ]
        return _name, measure_data

    @property
    def liquid(self):
        _name = "Объем"
        prefix = r""
        postfix = r""
        measures_data = [
            {
                "name": "Миллилитр",
                "symbols": r"мл|миллилитр|ml|milliliter",
                "ratio": 0.001,
                "prefix": prefix,
                "postfix": postfix,
            },
            {
                "name": "Литр",
                "symbols": r"литр|л|liter|l",
                "ratio": 1,
                "prefix": prefix,
                "postfix": postfix,
            },
        ]
        return _name, measures_data

    @property
    def mass(self):
        _name = "Вес"
        prefix = r""
        postfix = r""
        measures_data = [
            {
                "name": "Микрограмм",
                "symbols": r"мкг|микрограмм|µg|microgram",
                "ratio": 0.000000001,
                "prefix": prefix,
                "postfix": postfix,
            },
            {
                "name": "Миллиграмм",
                "symbols": r"мг|миллиграмм|mg|milligram",
                "ratio": 0.000001,
                "prefix": prefix,
                "postfix": postfix,
            },
            {
                "name": "Грамм",
                "symbols": r"г|гр|грамм|g|gram",
                "ratio": 0.001,
                "prefix": prefix,
                "postfix": "[. ]",
            },
            {
                "name": "Килограмм",
                "symbols": r"кг|килограмм|kg|kilogram",
                "ratio": 1,
                "prefix": prefix,
                "postfix": postfix,
            },
        ]
        return _name, measures_data

    @property
    def ME(self):
        _name = "Международные единицы"
        prefix = r""
        postfix = r""
        measures_data = [
            {
                "name": "МЕ",
                "symbols": r"ме|iu|ед|me",
                "ratio": 0.000001,
                "prefix": prefix,
                "postfix": postfix,
            },
            {
                "name": "Тысяча МЕ",
                "symbols": r"тыс.ме|th.iu|тыс.ед|тыс.me|т.ме|th.iu|т.ед|т.me",
                "ratio": 0.001,
                "prefix": prefix,
                "postfix": postfix,
            },
            {
                "name": "Миллион МЕ",
                "symbols": r"млн.ме|mln.iu|млн.ед|млн.me",
                "ratio": 1,
                "prefix": prefix,
                "postfix": postfix,
            },
        ]
        return _name, measures_data

    def _getNames(self, measures):
        return [measure["name"] for measure in measures]

    def getNames(self):
        measures_types = [
            self.memory,
            self.concByMilliliter,
            self.concPercent,
            self.liquid,
            self.mass,
            self.ME,
        ]

        names = []
        for measures in measures_types:
            names.extend(self._getNames(measures[1]))
        return names


class MeasureExtractor(Extractor):
    """
    Extract measures from rows by measure rule and make regex for them.
    Example: 15 мл -> extract "15"

    - measure_data - MeasuresData attribute (for special measure)
    - mode - combining mode of regex, can be 'triplet' or 'overall'
    - max_values - max count of extracted values
    - add_space - add extra space in end of the rows (for better extration by regex)
    returning dataframe wouldn't contains the extra space
    """

    def __init__(
        self,
        measure_data: MeasuresData,
        mode: str = "triplet",
        max_values: int = 0,
        add_space: bool = True,
    ):
        self._name = measure_data[0]
        self.measure_data = measure_data[1]
        self.mode = mode
        self.max_values = max_values
        self.add_space = add_space

    def _get_measures(self):
        if self.mode == "triplet":
            return Measures(self.measure_data).makeTriplets()
        elif self.mode == "overall":
            return Measures(self.measure_data).makeOverall()

    def _add_space(self, series: pd.Series) -> pd.Series:
        return series + " " if self.add_space else series

    def _show_status(self):
        print("Извлекаю характеристики типа:", self._name)

    def extract(self, data: pd.DataFrame, col: str) -> pd.DataFrame:
        """
        return dataframe with extra columns which depend of
        name of the measures (from MeasuresData attribute)
        """
        self._show_status()

        _data = self._add_space(data[col])
        measures = self._get_measures()

        for measure in measures:
            measureValues = extractMeasureValues(
                _data,
                measure,
                max_values=self.max_values,
            )

            regex = createMeasureRX(measureValues, measure)
            data = pd.concat([data, regex], axis=1)

        return data


if __name__ == "__main__":
    MD = MeasuresData()
    MD.getNames()
