from abc import ABC, abstractmethod
from tokenization import Token
from fuzzywuzzy import fuzz
import pandas as pd


class AbstractFuzzySearcher(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def search(self, tokens: set) -> dict:
        pass


class FuzzySearcher(AbstractFuzzySearcher):
    def __init__(self, fuzzy_threshold: int) -> None:
        self.fuzzy_threshold = fuzzy_threshold

    def _is_fuzzy_similar(self, token: Token, other_token: Token) -> bool:
        if token == other_token:
            # print(f"{token.value} == {other_token.value}")
            return True

        score = fuzz.WRatio(token.value, other_token.value)
        if score >= self.fuzzy_threshold:
            # print(f"{token.value} similar {other_token.value}")
            return True

        # print(f"{token.value} not similar {other_token.value}")

        return False

    def _search_similar(self, token: Token, other_tokens: set[Token]) -> None:
        for other_token in other_tokens:
            if self._is_fuzzy_similar(token, other_token):
                token.add_similar_token(other_token)
                other_token.add_similar_token(token)

    def search(self, left_tokens: pd.Series, right_tokens: pd.Series) -> None:
        left_tokens: set = set().union(*left_tokens.to_list())  # set of client tokens
        right_tokens: set = set().union(*right_tokens.to_list())  # set of site tokens

        for left_token in left_tokens:
            self._search_similar(left_token, right_tokens)

        return left_tokens.union(right_tokens)
