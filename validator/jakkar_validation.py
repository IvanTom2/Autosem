import pandas as pd
import re
import sys
import os
from nltk.tokenize import word_tokenize
from fuzzywuzzy import process as fuzz_process
from collections import Counter
from itertools import chain
from tqdm.auto import tqdm
from collections import namedtuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autosem.word_extraction import *

tqdm.pandas()


class Token(object):
    """
    Token object class.
    It's a simple word with some weight.

    - value - string value (word)
    - custom_weight - custom weight of this word (don't use manual)
    """

    def __init__(
        self,
        value: str,
        custom_weight: float = -1,
    ) -> None:
        self.value = value
        self.custom_weight = custom_weight

    def __eq__(self, other) -> bool:
        if isinstance(other, self.__class__):
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        else:
            raise ValueError("Can't compare this class")

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return f"{self.value} = {self.custom_weight}"

    def __repr__(self) -> str:
        return f"{self.value} = {self.custom_weight}"


class BasicTokenizer(object):
    """This class perform token's extraction by default NLTK tokenizer"""

    def __init__(self):
        pass

    def make_lower(self, token: str) -> str:
        return token.lower()

    def create_tokens(self, tokens: list[str]) -> list[Token]:
        tokens = [
            Token(
                value=self.make_lower(token),
                custom_weight=1,
            )
            for token in tokens
        ]
        return tokens

    def tokenize(
        self,
        data: pd.DataFrame,
        col: str,
        token_col_name: str,
    ) -> pd.DataFrame:
        """Return the dataframe with extra column <token_col_name>"""

        data[token_col_name] = data[col].apply(word_tokenize)
        data[token_col_name] = data[token_col_name].apply(self.create_tokens)
        return data


# it's simple collection for LanguageRules
# and weight of extracted tokens by them
WeightsRules = namedtuple("WeightRule", ["rules", "weight"])


class RegexCustomWeights:
    """
    This class contains config and weights for LanguageRules
    for future token's extraction

    - caps - weight for caps tokens
    - capital - weight for capital tokens
    - low - weight for low tokens
    - other - weight for other tokens
    - symbols - extra symbols for LanguageRules
    (for all types of extraction)
    - word_boundary - word boundary for LanguageRules
    (for all types of extraction)
    - custom_boundary - custom boundary for LanguageRules
    (for all types of extraction)
    """

    def __init__(
        self,
        caps: int,
        capital: int,
        low: int,
        other: int,
        symbols: str = "-",
        word_boundary: bool = True,
        custom_boundary: str = "",
    ) -> None:
        self.caps = caps
        self.capital = capital
        self.low = low
        self.other = other
        self.symbols = symbols

        self.word_boundary = word_boundary
        self.custom_boundary = custom_boundary

    def get_rules(self) -> dict:
        rules = {
            "caps": WeightsRules(
                {
                    "rule_name": "caps",
                    "join_words": False,
                    "onlyUpper": True,
                    "with_numbers": True,
                    "check_letters": True,
                    "symbols": self.symbols,
                    "word_boundary": self.word_boundary,
                    "custom_boundary": self.custom_boundary,
                },
                self.caps,
            ),
            "capital": WeightsRules(
                {
                    "rule_name": "capital",
                    "join_words": False,
                    "startUpper": True,
                    "with_numbers": True,
                    "check_letters": True,
                    "symbols": self.symbols,
                    "word_boundary": self.word_boundary,
                    "custom_boundary": self.custom_boundary,
                },
                self.capital,
            ),
            "low": WeightsRules(
                {
                    "rule_name": "low",
                    "join_words": False,
                    "onlyUpper": False,
                    "with_numbers": True,
                    "check_letters": True,
                    "symbols": self.symbols,
                    "word_boundary": self.word_boundary,
                    "custom_boundary": self.custom_boundary,
                },
                self.low,
            ),
            "other": WeightsRules(
                {
                    "rule_name": "other",
                    "join_words": False,
                    "with_numbers": True,
                    "symbols": self.symbols,
                    "word_boundary": self.word_boundary,
                    "custom_boundary": self.custom_boundary,
                },
                self.other,
            ),
        }
        return rules


class RegexTokenizer(BasicTokenizer):
    """
    This class perform custom token's extraction and
    token's weight distribution by LanguageRules.
    For config weights and rules used RegexCustomWeights.


    languages - dictionary of language : language weight for extraction
    weights_rules - RegexCustomWeights config
    """

    def __init__(
        self,
        languages: dict[str, int],
        weights_rules: RegexCustomWeights,
    ) -> None:
        self.languages = languages
        self.weights_rules = weights_rules.get_rules()

    def create_tokens(
        self,
        data: pd.DataFrame,
        token_col_name: str,
        weights_rules: WeightsRules,
        lang_weight: int,
    ) -> pd.DataFrame:
        rows: pd.Series = data[weights_rules.rules["rule_name"]]
        tokens = rows.apply(
            lambda _words: [
                Token(
                    value=word,
                    custom_weight=weights_rules.weight * lang_weight,
                )
                for word in _words
            ]
        )

        data[token_col_name] = data[token_col_name] + tokens
        return data

    def tokenize(
        self, data: pd.DataFrame, col: str, token_col_name: str
    ) -> pd.DataFrame:
        data[token_col_name] = [[] for _ in data.index]
        for language in self.languages:
            lang_weight = self.languages[language]
            for rule_name in self.weights_rules.keys():
                weights_rule = self.weights_rules[rule_name].rules

                extractor = WordsExtractor(
                    LanguageRules(
                        language,
                        **weights_rule,
                    ),
                    expand_spaces=True,
                    del_founded=True,
                )

                data = extractor.extract(data, col)
                data = self.create_tokens(
                    data, token_col_name, self.weights_rules[rule_name], lang_weight
                )
                data = data.drop(weights_rule["rule_name"], axis=1)

        return data


def del_rx(series: pd.Series):
    pass


def upload_data(
    validation_path: str,
    semantic_path: str = "",
) -> tuple[pd.Series, pd.Series]:
    def upload(path: str) -> pd.Series:
        if re.search(".csv$", path):
            data = pd.read_csv(path)
        else:
            data = pd.read_excel(path)
        return data

    semantic = upload(semantic_path) if semantic_path else None
    validation = upload(validation_path) if validation_path else None
    return semantic, validation


class FuzzyJakkarValidator(object):
    """
    Reworked version of Microsoft Fuzzy Lookup.

    This class perform text comparison by rows.
    At first, this algorith search similar tokens between two rows by Levenstein distance.
    Founded similar tokens transform in the same token.
    Then alghorith counts Jakkar similarity for the sets of preprocessed tokens.
    In this algorith used 2 types of token's weight:
    1) Custom token weight = custom
    2) Frequency weight = 1 / token frequency
    3) The end weight of token = custom token weight * frequency weight

    - tokenizer - the class which can perform tokenization.
    - symbols_to_del - delete this symbols from rows (before tokenization)
    - delete_rx - delete some words by regex
    (the dataframe should contains 'regex' column)
    - uniq_max_value - the treshold to determine "uniq" tokens
    (like single token in all rows)
    - uniq_penalty - penalty for "uniq" tokens (multiplier)
    - min_ratio - min treshold for the token's ration
    - max_ratio - max treshold for the token's ration,
    - word_min_length - minimum token len (should be off if used RegexTokenizer)
    - fuzzy_threshold - min treshold for determine tokens as similar
    - count_mark_by - mode for marks counting: choose type of divider for Jakkar
    (it can be 'union', 'site', 'client' - then intersection of token's sets
    would be divided on union of token's sets, just on site token's set or client token's set)
    - multiple_marks - use this if you want count with all types of dividers
    - save_ratio - use this if you want to save requency weights of tokens
    """

    def __init__(
        self,
        tokenizer,
        symbols_to_del: str = "'\"/",
        delete_rx: bool = False,
        uniq_max_value: int = 1,
        uniq_penalty: float = 0,
        min_ratio: float = 0,
        max_ratio: float = 1,
        word_min_length: int = 3,
        fuzzy_threshold: int = 65,
        count_mark_by: str = "union",
        multiple_marks: bool = False,
        save_ratio: bool = False,
    ):
        self.tokenizer = tokenizer
        self.delete_rx = delete_rx
        self.symbols_to_del = symbols_to_del
        self.uniq_max_value = uniq_max_value
        self.uniq_penalty = uniq_penalty
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
        self.word_min_length = word_min_length
        self.fuzzy_threshold = fuzzy_threshold
        self.count_mark_by = count_mark_by
        self.multiple_marks = multiple_marks
        self.save_ratio = save_ratio

    def _fuzzy_change(self, token: Token, other_tokens: set[Token]):
        if not other_tokens:
            return token

        if token not in other_tokens:
            token_value = token.value
            other_tokens_values = [token.value for token in other_tokens]

            token_value_changed = fuzz_process.extractOne(
                token_value,
                other_tokens_values,
            )

            if token_value_changed[1] >= self.fuzzy_threshold:
                new_token_set = other_tokens - (other_tokens - {token_value_changed[0]})
                new_token = new_token_set.pop()

                # print(f'Токен {token.value} изменен на {new_token.value}')
                return new_token
        return token

    def _fuzzy(self, row: pd.Series) -> pd.Series:
        # Сейчас изменение токенов применяется только для правых (site) токенов
        # TODO: сделать изменение токенов на выбор

        ctokens = row["ctokens"]  # set of client tokens
        stokens = row["stokens"]  # set of site tokens

        row["stokens"] = {self._fuzzy_change(stoken, ctokens) for stoken in stokens}
        return row

    def _filter(self, series: pd.Series) -> pd.Series:
        return series.apply(
            lambda tokens: list(
                filter(lambda token: len(token.value) >= self.word_min_length, tokens)
            )
        )

    def _make_set(self, series: pd.Series) -> pd.Series:
        return series.apply(lambda tokens: set(tokens))

    def _lower(self, series: pd.Series) -> pd.Series:
        return series.apply(lambda _words: list(map(str.lower, _words)))

    def _uniq_penalty(self, value: int) -> float:
        value_rate = 1 / value
        value_rate = self.min_ratio if value_rate < self.min_ratio else value_rate
        value_rate = self.max_ratio if value_rate > self.max_ratio else value_rate

        if self.uniq_max_value:
            if value <= self.uniq_max_value:
                value_rate = value_rate * self.uniq_penalty
        return value_rate

    def _make_ratio(self, counts: dict[str]) -> dict:
        ratio = {}
        for key, value in counts.items():
            rate = self._uniq_penalty(value)
            ratio[key] = rate
        return ratio

    def _count_ratio(self, ctokens: pd.Series, stokens: pd.Series) -> dict[str, int]:
        # TODO: drop duplicates
        tokens = stokens.to_list() + ctokens.to_list()
        tokens = list(chain(*map(list, tokens)))
        tokens_values = [token.value for token in tokens]

        counts = Counter(tokens_values)
        ratio = self._make_ratio(counts)
        return ratio

    def _find_ratio(self, tokens: set[Token]):
        tokens_rates = [
            self.ratio[token.value] * token.custom_weight for token in tokens
        ]
        return tokens_rates

    def _count_mark(self, row: pd.Series) -> float:
        def try_count_mark(intersect: set[Token], union: set[Token]) -> float:
            try:
                mark = sum(intersect) / sum(union)
            except Exception:
                mark = 0
            finally:
                return mark

        intersect = row["ctokens"].intersection(row["stokens"])

        # print([token.value for token in row["ctokens"]])
        # print([token.value for token in row["stokens"]])
        # print([token.value for token in intersect])
        # print("\n")

        if self.count_mark_by == "union":
            union = row["ctokens"].union(row["stokens"])
        elif self.count_mark_by == "client":
            union = row["ctokens"]
        elif self.count_mark_by == "site":
            union = row["stokens"]
        else:
            raise ValueError(
                f"There are not such choice: {self.count_mark_by}. Choices: union, client, site."
            )

        intersect = self._find_ratio(intersect)
        union = self._find_ratio(union)

        mark = try_count_mark(intersect, union)
        return mark

    def _count_multiple_marks(self, row: pd.Series) -> list[float]:
        intersect = row["ctokens"].intersection(row["stokens"])

        unions = [
            row["ctokens"].union(row["stokens"]),
            row["ctokens"],
            row["stokens"],
        ]

        _intersect = sum(self._find_ratio(intersect))
        marks = [(_intersect / sum(self._find_ratio(union))) for union in unions]
        return marks

    def _tokenize(
        self, data: pd.DataFrame, col: str, token_col_name: str
    ) -> pd.DataFrame:
        data = self.tokenizer.tokenize(data, col, token_col_name)
        return data

    def _delete_rx(self):
        pass

    def _create_working_rows(
        self,
        validation: pd.DataFrame,
        client_column: str,
        site_column: str,
    ) -> pd.DataFrame:
        symbols_to_del = "|".join(list(self.symbols_to_del))

        validation["_client"] = validation[client_column].str.replace(
            symbols_to_del, "", regex=True
        )
        validation["_site"] = validation[site_column].str.replace(
            symbols_to_del, "", regex=True
        )
        return validation

    def _delete_working_rows(self, validation: pd.DataFrame) -> pd.DataFrame:
        self._progress_ind("end")
        validation.drop(["_client", "_site"], axis=1, inplace=True)
        # validation.drop(["ctokens", "stokens"], axis=1, inplace=True)
        return validation

    def process_tokenization(self, validation: pd.DataFrame) -> pd.DataFrame:
        self._progress_ind("client_tokens")
        validation = self._tokenize(validation, "_client", "ctokens")

        self._progress_ind("site_tokens")
        validation = self._tokenize(validation, "_site", "stokens")

        return validation

    def process_preprocessing(self, validation: pd.DataFrame) -> pd.DataFrame:
        if self.word_min_length:
            self._progress_ind("make_filter")
            validation["ctokens"] = self._filter(validation["ctokens"])
            validation["stokens"] = self._filter(validation["stokens"])

        self._progress_ind("make_set")
        validation["ctokens"] = self._make_set(validation["ctokens"])
        validation["stokens"] = self._make_set(validation["stokens"])

        return validation

    def process_ratio(self, validation: pd.DataFrame) -> pd.DataFrame:
        # TODO: recount token custom weight MUSTHAVE!
        # проблема - у токенов слева и справа могут быть одинаковые значение, но разные кастомные веса

        self._progress_ind("make_fuzzy")
        validation = validation.progress_apply(self._fuzzy, axis=1)

        self._progress_ind("make_ratio")
        self.ratio = self._count_ratio(
            validation["ctokens"],
            validation["stokens"],
        )

        return validation

    def process_marks_counting(self, validation: pd.DataFrame) -> pd.DataFrame:
        if self.multiple_marks:
            marks = validation.progress_apply(self._count_multiple_marks, axis=1)

            validation["mark_union"] = marks.str[0]
            validation["mark_client"] = marks.str[1]
            validation["mark_site"] = marks.str[2]
        else:
            validation["mark"] = validation.progress_apply(self._count_mark, axis=1)

        return validation

    def _save_ratio(self) -> None:
        df_ratio = pd.DataFrame(data=self.ratio.items(), index=range(len(self.ratio)))
        df_ratio.to_excel("tokens.xlsx")

    def _progress_ind(self, indicator: str) -> None:
        match indicator:
            case "start":
                print("Start Fuzzy Jakkar matching")
            case "client_tokens":
                print("Tokenize client tokens")
            case "site_tokens":
                print("Tokenize site tokens")
            case "make_filter":
                print("Make tokens filter")
            case "make_set":
                print("Make set of tokens")
            case "make_fuzzy":
                print("Start fuzzy search")
            case "make_ratio":
                print("Start count match ratio")
            case "end":
                print("End the validation process: save output")
            case "delete_rx":
                print("Deleting elements from rows by regex")

    def validate(
        self,
        validation: pd.DataFrame,
        semantic: pd.DataFrame = pd.DataFrame(),
        client_column: str = "Название",
        site_column: str = "Строка валидации",
        regex_column: str = "Regex",
    ) -> pd.DataFrame:
        """Start validation funcs"""

        self._progress_ind("start")
        validation = self._create_working_rows(
            validation,
            client_column,
            site_column,
        )

        if self.delete_rx:
            self._progress_ind("delete_rx")

        validation = self.process_tokenization(validation)
        validation = self.process_preprocessing(validation)
        validation = self.process_ratio(validation)
        validation = self.process_marks_counting(validation)

        self._save_ratio()

        validation = self._delete_working_rows(validation)
        return validation


if __name__ == "__main__":
    weights_rules = RegexCustomWeights(
        caps=1,
        capital=2,
        low=1,
        other=1,
        symbols="",
        custom_boundary=r"\s",
    )
    tokenizer = RegexTokenizer(
        {"english": 2, "russian": 1},
        weights_rules=weights_rules,
    )

    validator = FuzzyJakkarValidator(
        tokenizer,
        word_min_length=3,
        min_ratio=0.1,
        max_ratio=0.5,
        fuzzy_threshold=75,
        count_mark_by="union",
        multiple_marks=False,
    )

    semantic, validation = upload_data(
        # semantic_path="/home/mainus/BrandPol/validator/semantic.csv",
        validation_path=r"C:\Users\tomilov-iv\Desktop\BrandPol\validator\neknigi.xlsx",
    )

    # validation = validation[:10]

    result = validator.validate(
        validation,
        client_column="Название товара клиента",
        site_column="Строка валидации",
    )

    result.to_excel("neknigi_jakkar_output.xlsx", index=False)
