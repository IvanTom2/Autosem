import pandas as pd
import sys
import os
import regex as re
from typing import Union


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from autosem.autosem_funcs.word_extraction_funcs import (
    LanguageRules,
    extractWords,
    deleteWords,
    extractWordsWithMultipleLangsLetters,
)
from common import (
    Extractor,
    wordsCleaner,
    wordsFilter,
    wordsStemming,
    wordsJoin,
    parse_rx,
)
from measures_extraction import MeasuresData


class WordsExtractor(Extractor):
    def __init__(
        self,
        rules: LanguageRules,
        expand_spaces: bool = False,
        del_founded: bool = False,
    ):
        self.rules = rules
        self.expand_spaces = expand_spaces
        self.del_founded = del_founded

    def _preprocess(
        self,
        words: pd.Series,
    ) -> pd.Series:
        words = wordsCleaner(words)
        words = wordsFilter(
            words,
            min_length=self.rules.min_length,
            max_words=self.rules.max_words,
        )

        if self.rules.stemming:
            words = wordsStemming(
                words,
                language=self.rules.language_name,
            )

        if self.rules.join_words:
            words = wordsJoin(words, joiner=self.rules.joiner)
        return words

    def _extract(self, data: pd.DataFrame, col: str) -> pd.DataFrame:
        words = extractWords(data["_rows"], self.rules)
        if self.del_founded:
            data["_rows"] = deleteWords(data["_rows"], self.rules)
            data[col] = data["_rows"].str.replace(r"[ ]+", r" ", regex=True)

        words = self._preprocess(words)
        return words

    def extract(
        self,
        data: pd.DataFrame,
        col: str,
        return_mode: str = "dataframe",
    ) -> pd.DataFrame:
        if return_mode not in ["series", "dataframe"]:
            raise ValueError("return_mode should be 'series' or 'dataframe'.")

        data["_rows"] = data[col]
        if self.expand_spaces:
            data["_rows"] = "  " + data["_rows"] + "  "
            data["_rows"] = data["_rows"].str.replace(" ", " " * 3)

        words = self._extract(data, col)
        data.drop("_rows", axis=1, inplace=True)
        if return_mode == "series":
            return words
        elif return_mode == "dataframe":
            data[self.rules.rule_name] = words
            return data


class StraightWordExtractor(Extractor):
    def __init__(
        self,
        rules: list[LanguageRules],
        straight: bool = False,
        main_rule: int = 0,
        expand_spaces: bool = False,
        del_founded: bool = False,
    ):
        if straight and not isinstance(rules, list):
            rules = [rules]

        self.rules = rules
        self.straight = straight
        self.main_rule = main_rule
        self.expand_spaces = expand_spaces
        self.del_founded = del_founded

    def _preprocess(
        self,
        words: pd.Series,
        rules: LanguageRules,
    ) -> pd.Series:
        words = wordsCleaner(words)
        words = wordsFilter(
            words,
            min_length=rules.min_length,
            max_words=rules.max_words,
        )

        if rules.stemming:
            words = wordsStemming(
                words,
                language=rules.language_name,
            )

        if rules.join_words:
            words = wordsJoin(words, joiner=rules.joiner)
        return words

    def _straight(self, data: pd.DataFrame, newcol: str):
        words = extractWordsWithMultipleLangsLetters(data["_rows"], self.rules)
        data[newcol] = self._preprocess(words, self.rules[self.main_rule])

        return data

    def extract(
        self,
        data: pd.DataFrame,
        col: str,
        newcol: str = "straight",
    ) -> pd.DataFrame:
        data["_rows"] = data[col]
        if self.expand_spaces:
            data["_rows"] = "  " + data["_rows"] + "  "
            data["_rows"] = data["_rows"].str.replace(" ", " " * 3)

        data = self._straight(data, newcol)

        data.drop("_rows", axis=1, inplace=True)
        return data


class ValuesExtractorByRx(Extractor):
    """
    measure_data: Union[str, MeasuresData] - can be str or MeasureData
    max_values: int = 0 - it's constraint of extracted values by regex (filter regexes)
    """

    def __init__(
        self,
        measure_data: Union[str, MeasuresData],
        max_values: int = 0,
    ):
        self.measure_data = measure_data
        self.max_values = max_values

    def _try_search(
        self,
        pattern: str,
        string: str,
    ) -> str:
        output = ""
        try:
            output = re.search(pattern, string, flags=re.IGNORECASE)[0]
        except Exception:
            output = ""
        finally:
            return output.strip()

    def _extract(self, row: pd.Series, col: str) -> pd.Series:
        values = [
            self._try_search(pattern, row[col]) for pattern in row["regex_extracted"]
        ]
        row["out"] = ";".join(values)
        return row

    def extract(
        self,
        data: pd.DataFrame,
        col: str,
    ) -> pd.Series:
        if isinstance(self.measure_data, str):
            measure_names = [self.measure_data]
        else:
            measure_names = [dct["name"] for dct in self.measure_data[1]]

        regex = data[[col]]
        regex["regex"] = data[measure_names[0]]
        for measure_name in measure_names[1:]:
            regex["regex"] += data[measure_name]
        regex["regex"] = regex["regex"].fillna("")

        regex = parse_rx(regex, "regex", "regex_extracted")
        if self.max_values:
            regex["regex_extracted"] = regex["regex_extracted"].str[: self.max_values]

        regex = regex.apply(self._extract, axis=1, args=(col,))
        return regex["out"]


if __name__ == "__main__":
    data = pd.DataFrame(data=["Привет Мир! Ваня228 Ajax Ajax17"], columns=["Название"])

    ru = LanguageRules(
        "russian", rule_name="rus", word_boundary=True, with_numbers=True
    )
    eng = LanguageRules(
        "english", rule_name="eng", word_boundary=True, with_numbers=True
    )

    ru_extractor = WordsExtractor(rules=ru)
    eng_extractor = WordsExtractor(rules=eng)
    straigth_extractor = StraightWordExtractor([ru, eng])

    d = ru_extractor.extract(data, "Название")
    d = eng_extractor.extract(data, "Название")
    d = straigth_extractor.extract(data, "Название")
    print(d)
