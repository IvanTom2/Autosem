from abc import ABC, abstractmethod
import pandas as pd
from nltk.tokenize import word_tokenize
from collections import namedtuple
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from autosem.word_extraction import *


def indexer(start: int = 0) -> int:
    num = start
    while True:
        yield num
        num += 1


class AbstractToken(ABC):
    def __init__(self, value) -> None:
        self.original_value = str(value)
        self.value = str(value).lower()
        self.similar_tokens = set()

    @abstractmethod
    def add_similar_token(self):
        pass

    @abstractmethod
    def _is_similar(self):
        pass


class Token(AbstractToken):
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
        self.original_value = str(value)
        self.value = str(value).lower()
        self.custom_weight = custom_weight

        self.similar_tokens = set()
        self.add_similar_token(self)

    def add_similar_token(self, token):
        self.similar_tokens.add(token)

    @property
    def get_custom_weight(self):
        return abs(self.custom_weight)

    def _is_similar(self, other_token: AbstractToken) -> bool:
        if self.similar_tokens:
            if other_token in self.similar_tokens:
                return True
        if other_token.similar_tokens:
            if self in other_token.similar_tokens:
                return True
        return False

    def __eq__(self, other: AbstractToken) -> bool:
        if isinstance(other, AbstractToken):
            if self.value == other.value:
                return True
            if self._is_similar(other):
                return True
            return False

        else:
            raise ValueError("Can't compare this class")

    def __hash__(self) -> int:
        return hash(self.value)

    def __str__(self) -> str:
        return f"{self.original_value} = {self.custom_weight}"

    def __repr__(self) -> str:
        return f"{self.original_value} = {self.custom_weight}"


WeightsRules = namedtuple("WeightRule", ["rules", "weight"])


class RegexCustomWeights(object):
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


class AbstractTokenizer(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def tokenize(self):
        pass


class BasicTokenizer(AbstractTokenizer):
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
        indexer=indexer(0),
    ) -> None:
        self.languages = languages
        self.weights_rules = weights_rules.get_rules()
        self.indexer = indexer

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


if __name__ == "__main__":
    token1 = Token("abc")
    token2 = Token("abc")
    token3 = Token("ddd")

    print(token1 == token2)
