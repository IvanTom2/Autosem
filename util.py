import pandas as pd
import re
import os

from autosem.measures_extraction import MeasuresData


def upload(filename: str):
    dir_path = os.path.dirname(__file__) + r"\data\input"
    filename = dir_path + rf"\{filename}"
    if re.search(".xlsx$", filename):
        data = pd.read_excel(filename)
    elif re.search(".csv$", filename):
        data = pd.read_csv(filename)
    return data


def extracting(
    series: pd.Series,
    excludeSeries: pd.Series = pd.Series(dtype=str),
    lang_symbols: str = "а-яёa-z",
    num_symbols: str = "0-9",
    symbols: str = "",
    check_lang: bool = False,
    check_num: bool = False,
    check_symbols: bool = False,
    max_words: int = 0,
    joiner: str = "|",
):
    def _checkSymbols(extract: pd.Series, symbols):
        extract = extract.apply(
            lambda _words: [word for word in _words if re.search(f"[{symbols}]", word)]
        )
        return extract

    def exclude_series(series: pd.Series, excludeSeries: pd.Series):
        def _exclude(df: pd.DataFrame):
            string = df.data
            for excl in df.to_exclude:
                string = string.replace(excl, "")
            return string

        excludeSeries = excludeSeries.str.lower()
        excludeSeries_set = excludeSeries.astype(str).apply(lambda x: set(x.split()))

        excludeDf = pd.DataFrame()
        excludeDf["data"] = series
        excludeDf["to_exclude"] = excludeSeries_set

        series = excludeDf.apply(_exclude, axis=1)
        return series

    rx = f"[{lang_symbols}{num_symbols}{symbols}]+"

    series = series.str.lower()
    if len(excludeSeries) > 0:
        series = exclude_series(series, excludeSeries)

    extract = series.str.findall(rx)
    extract = _checkSymbols(extract, lang_symbols) if check_lang else extract
    extract = _checkSymbols(extract, num_symbols) if check_num else extract
    extract = _checkSymbols(extract, symbols) if check_symbols else extract

    if max_words:
        extract = extract.str[:max_words]

    extract = extract.str.join(joiner)
    return extract


def get_semantic_template():
    data = pd.DataFrame(
        columns=[
            "Название",
            "Поисковый запрос",
            "Плюс-слова",
            "Минус-слова",
            "Regex",
            "Note",
            "Штрихкод",
            "Brand",
            "Категория",
            "Категория 2",
            "Название клиента",
            "Ссылка на фото",
            "Штрихкод",
        ]
    )

    return data


def save(data: pd.DataFrame, filename: str) -> None:
    dir_path = os.path.dirname(__file__) + r"\data\output"
    filename = dir_path + rf"\{filename}"
    data.to_excel(filename, index=False)


def concat_rx(data: pd.DataFrame) -> pd.DataFrame:
    names = [
        "Исключающее количество",
        "Исключающее количество (№)",
        "Количество",
        "Количество (№)",
    ]
    names.extend(MeasuresData().getNames())
    names = [name for name in names if name in list(data.columns)]

    data["regex"] = data[names].agg("".join, axis=1)
    return data
