import pandas as pd
import math
from collections import namedtuple
import re


Measure = namedtuple(
    "Measure",
    [
        "name",
        "symbols",
        "ratio",
        "prefix",
        "postfix",
    ],
)

MeasureNGram = namedtuple(
    "MeasureNGram",
    [
        "position",
        "Measures",
    ],
)


def makeMeasureNGram(
    ngram_data: list[Measure],
    main_measure_name: str,
) -> list[Measure]:
    def countRatio(ratio, currentMeasureRatio):
        # TODO - здесь может быть скрыт баг в round()
        newRatio = ratio / currentMeasureRatio
        newRatio = newRatio if newRatio < 1 else round(newRatio)
        return newRatio

    def findPos(ngram_data, main_measure_name):
        position = 0
        for index in range(len(ngram_data)):
            if ngram_data[index].name == main_measure_name:
                position = index
        return position

    position = findPos(ngram_data, main_measure_name)

    currentMeasureRatio = ngram_data[position].ratio
    measureTripletData = [
        Measure(
            measure.name,
            measure.symbols,
            countRatio(measure.ratio, currentMeasureRatio),
            measure.prefix,
            measure.postfix,
        )
        for measure in ngram_data
    ]

    return MeasureNGram(position, measureTripletData)


class Measures(object):
    def __init__(self, measures_data) -> None:
        self.measures = [self.setupMeasure(measure) for measure in measures_data]

    def setupMeasure(self, measure):
        def _try(key):
            try:
                _return = measure[key]
            except Exception:
                _return = ""
            finally:
                return _return

        return Measure(
            measure["name"],
            measure["symbols"],
            measure["ratio"],
            _try("prefix"),
            _try("postfix"),
        )

    def makeTriplets(self):
        triplets = []
        for measure_index in range(len(self.measures)):
            main_measure_name = self.measures[measure_index].name

            if measure_index == 0:
                triplet_data = self.measures[measure_index : measure_index + 2]
                feature = makeMeasureNGram(triplet_data, main_measure_name)

            elif measure_index == len(self.measures) - 1:
                triplet_data = self.measures[measure_index - 1 : measure_index + 1]
                feature = makeMeasureNGram(triplet_data, main_measure_name)

            else:
                triplet_data = self.measures[measure_index - 1 : measure_index + 2]
                feature = makeMeasureNGram(triplet_data, main_measure_name)

            triplets.append(feature)

        return triplets

    def makeOverall(self):
        overall = []
        for measure_index in range(len(self.measures)):
            main_measure_name = self.measures[measure_index].name
            overall_data = self.measures[:]

            feature = makeMeasureNGram(overall_data, main_measure_name)
            overall.append(feature)

        return overall


def _makeDefaultRX(measure: Measure, value: str) -> str:
    symbols = measure.symbols
    prefix = measure.prefix
    postfix = measure.postfix

    rx = rf"{value}\s*?(?:{symbols})"
    rx = rf"{rx}(?:{postfix})" if postfix else rx
    rx = rf"(?:{prefix}){rx}" if prefix else rx

    return rx


def extractMeasureValues(
    series: pd.Series,
    nGram: MeasureNGram,
    max_values: int = 0,
):
    """Look up in lower case"""
    rx = _makeDefaultRX(nGram.Measures[nGram.position], "(\d*[,.]?\d+)")

    # TODO: deal with re.IGNORECASE
    measureValues = series.str.lower().str.findall(rx, flags=re.IGNORECASE)
    measureValues = measureValues.apply(
        lambda words: list(map(lambda word: word.replace(",", "."), words))
    )

    if max_values:
        measureValues = measureValues.apply(lambda x: x[:max_values])

    return measureValues


def createMeasureRX(measureValues: pd.Series, nGram: MeasureNGram):
    def transform(values, nGram):
        def prepValue(value):
            if value >= 1:
                # TODO - хардкод - может привести к ошибкам
                value = re.sub(r"\.0$", "", str(value))
            else:
                value = str(value)

            value = value.replace(".", "[,.]")
            return "\D" + value

        output = []
        for value in values:
            measure_rx = "(?=.*("
            for measure in nGram.Measures:
                val = value / measure.ratio
                if math.isclose(val, round(val)):
                    val = round(val)

                measure_rx += _makeDefaultRX(measure, prepValue(val)) + "|"

            measure_rx = re.sub("\|$", "", measure_rx) + "))"
            output.append(measure_rx)
        return output

    name = nGram.Measures[nGram.position].name
    measureValues.rename(name, inplace=True)

    measureRX = measureValues.apply(lambda x: list(map(float, x)))
    measureRX = measureRX.apply(transform, args=(nGram,))
    measureRX = measureRX.str.join("")

    return measureRX


def extractSizeMeasureValues(
    series: pd.Series,
    sep: str = "[xх]",
    measure: str = "",
):
    _int = r"\d*[.,]?\d+"
    _measure = rf"\s*?(?:{measure})?\s*?"

    rx = rf"({_int}{_measure}{sep}{_int}){_measure}{sep}?"

    measureValues = series.str.findall(rx)
    measureValues = measureValues.apply(
        lambda words: list(map(lambda word: word.replace(",", "."), words))
    )

    if measure:
        measureValues = measureValues.apply(
            lambda sizes: [size.replace(measure, "") for size in sizes]
        )

    measureValues = measureValues.apply(
        lambda sizes: [re.split(sep, size) for size in sizes]
    )

    return measureValues


def createSizeMeasureRX(
    measureValues: pd.Series,
    sep: str,
    measure: str,
    swap: bool = False,
):
    ### (?=.*(?=.*(10х10|100х100))|((?=.*(10мм)(?=.*(10 мм)))))

    # TODO - добавить множитель для изменения метров в см и т.д.

    measureValues = measureValues.apply(
        lambda sizes: [[f"\D?{s.replace('.', '[,.]')}" for s in size] for size in sizes]
    )

    # TODO - добавить swap - смена характеристик местами
    measureValues = measureValues.apply(
        lambda sizes: [f"\s*?(?:{measure})?\s*?{sep}".join(size) for size in sizes]
    )

    return measureValues
