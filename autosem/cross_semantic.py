import pandas as pd
import re
import copy
from tqdm import tqdm

from autosem_funcs.cross_semantic_funcs import BasicCrosser
from common import del_rx
from word_extraction import *


class Crosser(BasicCrosser):
    """
    This class can perform cross-minus and
    cross-intersection operations for
    find plus and minus words between rows.
    At first, it extract tokens (words) by custom self rules.

    - make_cross_minus - run cross-minus operation
    - make_cross_intersect - run cross-intersect operation
    - min_length - min lenght of extracted tokens (words)
    - max_words - max count of extracted tokens (words)
    - stemming - apply stemming for extracted tokens (words)
    - stemming_languages - list of stemming languages
    - dop_symbols - extra symbols, which can be contained in tokens (words)
    - join_words - join words after cross-operations
    - joiner - symbol for joining
    - delete_rx - if you want do delete elements by rx
    (in this case dataframe should contains 'regex' column)
    """

    def __init__(
        self,
        make_cross_minus: bool = True,
        make_cross_intersect: bool = True,
        min_length: int = 0,
        max_words: int = 0,
        stemming: bool = False,
        stemming_languages: list[str] = ["russian"],
        dop_symbols: str = "-",
        join_words: bool = True,
        joiner: str = "|",
        delete_rx: bool = True,
    ) -> None:
        BasicCrosser.__init__(self)

        self.make_cross_minus = make_cross_minus
        self.make_cross_intersect = make_cross_intersect
        self.dop_symbols = dop_symbols
        self.joiner = joiner
        self.min_length = min_length
        self.max_words = max_words
        self.stemming = stemming
        self.stemming_languages = stemming_languages
        self.join_words = join_words
        self.delete_rx = delete_rx

    def _checkout(self, row: str, rx: str, plus: bool) -> bool:
        if plus:
            checkout = True if re.search(list(rx)[0], row, re.IGNORECASE) else False
        else:
            checkout = False if re.search(list(rx)[0], row, re.IGNORECASE) else True
        return checkout

    def _call_cross_minus(
        self,
        data: pd.DataFrame,
        col: str,
        current_set: set,
        other_set: set,
        index: int,
        rest_index: int,
    ) -> None:
        cross_minus = self.get_cross_minus(current_set, other_set)
        if cross_minus:
            if self._checkout(data.at[index, col], cross_minus, plus=False):
                data.at[index, "cross_minus"].update(cross_minus)
            if self._checkout(data.at[rest_index, col], cross_minus, plus=True):
                data.at[rest_index, "cross_plus"].update(cross_minus)

    def _call_cross_intersect(
        self,
        data: pd.DataFrame,
        col: str,
        current_set: set,
        other_set: set,
        index: int,
        rest_index: int,
    ) -> None:
        cross_intersect = self.get_cross_intersect(current_set, other_set)
        if cross_intersect:
            if self._checkout(data.at[index, col], cross_intersect[0], plus=True):
                data.at[index, "cross_intersect"].update(cross_intersect[0])
            if self._checkout(data.at[index, col], cross_intersect[1], plus=True):
                data.at[rest_index, "cross_intersect"].update(cross_intersect[1])

    def _setup(self, data: pd.DataFrame) -> pd.DataFrame:
        for col in self.columns:
            data[col] = [set() for _ in range(len(data))]
        return data

    def _to_list(self, data: pd.DataFrame) -> pd.DataFrame:
        for col in self.columns:
            data[col] = data[col].apply(lambda x: list(x))
        return data

    def _preprocess(self, words: pd.Series) -> pd.Series:
        words = wordsFilter(
            words,
            min_length=self.min_length,
            max_words=self.max_words,
        )

        if self.stemming:
            for language in self.stemming_languages:
                words = wordsStemming(
                    words,
                    language=language,
                )

        if self.join_words:
            words = wordsJoin(words, joiner=self.joiner)
        return words

    def _prerocess_columns(self, data: pd.DataFrame) -> pd.DataFrame:
        for col in self.columns:
            data[col] = self._preprocess(data[col])
        return data

    def _del_rx(self, data: pd.DataFrame, col: str) -> pd.DataFrame:
        if self.delete_rx:
            data = del_rx(data, col)
        else:
            data["row"] = data[col]
        return data

    def _join(self, data):
        for col in self.columns:
            data[col] = wordsJoin(data[col])
        return data

    def extract(self, data: pd.DataFrame, col: str) -> pd.DataFrame:
        """
        Return the dataframe with three extra columns:
        1) cross-minus
        2) cross-plus
        3) cross-intersect
        """

        data = self._setup(data)
        data = self._del_rx(data, col)
        data["tokens"] = self.get_tokens(data, "row", self.dop_symbols)

        indexes = set(data.index)
        for index in indexes:
            current_set = data.at[index, "tokens"]
            rest_indexes = indexes - set([index])  # can be profiled

            for rest_index in rest_indexes:
                other_set = data.at[rest_index, "tokens"]

                if self.make_cross_minus:
                    self._call_cross_minus(
                        data, "row", current_set, other_set, index, rest_index
                    )
                if self.make_cross_intersect:
                    self._call_cross_intersect(
                        data, "row", current_set, other_set, index, rest_index
                    )

        data = self._to_list(data)
        data = self._join(data)
        data.drop("tokens", axis=1, inplace=True)
        return data


class CrosserPro(Crosser):
    """
    This class can perform cross-minus and
    cross-intersection operations for
    find plus and minus words between rows.
    At first, it extract tokens (words) by custom LanguageRules.
    The token's extraction is more complicated than in Crosser.

    - rules - list of LanguageRules
    - make_cross_minus - run cross-minus operation
    - make_cross_intersect - run cross-intersect operation
    - delete_rx - if you want do delete elements by rx
    (in this case dataframe should contains 'regex' column)
    - process_nearest - sort and process nearest N left and right rows
    """

    def __init__(
        self,
        rules: list[LanguageRules],
        make_cross_minus: bool = True,
        make_cross_intersect: bool = True,
        delete_rx: bool = True,
        process_nearest: int = 0,
    ):
        BasicCrosser.__init__(self)

        self.rules = self._setup_rules(rules)
        self.make_cross_minus = make_cross_minus
        self.make_cross_intersect = make_cross_intersect
        self.delete_rx = delete_rx
        self.process_nearest = process_nearest

        self.extractors = [WordsExtractor(rule) for rule in self.rules]

    def _setup_rules(self, rules: list[LanguageRules]) -> list[LanguageRules]:
        rules = copy.deepcopy(rules)
        rules = [rules] if not isinstance(rules, list) else rules
        for rule in rules:
            rule.join_words = False
        return rules

    def _show_status(self):
        print("Извелечение слов по кросс-семантике")

    def extract(self, data: pd.DataFrame, col: str):
        """
        IF YOU USE delete_rx=True parameter YOU SHOULD concat_rx(data)
        BEFORE RUN THIS METHOD

        Return the dataframe with three extra columns:
        1) cross-minus
        2) cross-plus
        3) cross-intersect
        """

        self._show_status()

        data = self._setup(data)
        data = self._del_rx(data, col)
        data = self.get_tokens_pro(data, "row", self.extractors)

        if self.process_nearest:
            data = data.sort_values(by=[col])

        indexes = list(data.index)
        for pos_index in tqdm(range(len(indexes))):
            index = indexes[pos_index]
            current_set = data.at[index, "tokens"]

            rest_indexes = indexes[:]  # or use copy.copy(indexess)
            if self.process_nearest:
                rest_indexes = indexes[
                    max(0, pos_index - self.process_nearest) : min(
                        len(indexes), pos_index + self.process_nearest + 1
                    )
                ]

            if index in rest_indexes:
                rest_indexes.remove(index)  # can be profiled?

            for rest_index in rest_indexes:
                other_set = data.at[rest_index, "tokens"]

                if self.make_cross_minus:
                    self._call_cross_minus(
                        data, col, current_set, other_set, index, rest_index
                    )
                if self.make_cross_intersect:
                    self._call_cross_intersect(
                        data, col, current_set, other_set, index, rest_index
                    )

        data = self._to_list(data)
        data = self._join(data)
        data.drop("tokens", axis=1, inplace=True)
        return data


if __name__ == "__main__":
    # data = pd.read_excel(r'C:\Users\tomilov-iv\Desktop\BrandPol\cross_sem\CommonSem.xlsx')

    data = pd.DataFrame()
    data.at[0, "Название"] = "Апельсин"
    data.at[1, "Название"] = "Апельсин красный"
    data.at[2, "Название"] = "Апельсин красный свежий"
    data.at[3, "Название"] = "Айфон красный"
    data.at[4, "Название"] = "Айфон синий"
    data.at[5, "Название"] = "Айфон зеленый"

    ru = LanguageRules(
        "russian", word_boundary=True, with_numbers=True, join_words=False
    )

    crosser = Crosser(
        make_cross_minus=True,
        make_cross_intersect=True,
        min_length=0,
        max_words=0,
        stemming=False,
        stemming_languages=["russian"],
        dop_symbols="-",
        join_words=True,
        joiner="|",
        delete_rx=False,
    )

    crosserPro = CrosserPro(
        [ru],
        make_cross_minus=True,
        make_cross_intersect=True,
        delete_rx=False,
    )

    # data = crosser.extract(data, "Название")
    data = crosserPro.extract(data, "Название")

    # data.to_excel('output.xlsx', index=False)
