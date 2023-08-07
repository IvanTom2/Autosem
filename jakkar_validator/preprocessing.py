import pandas as pd
from abc import ABC


class AbstractPreprocessor(ABC):
    def __init__(self) -> None:
        pass

    def preprocess(self, series: pd.Series) -> pd.Series:
        pass


class Preprocessor(AbstractPreprocessor):
    def __init__(
        self,
        word_min_length: int,
    ) -> None:
        self.word_min_length = word_min_length

    def _filter(self, series: pd.Series) -> pd.Series:
        return series.apply(
            lambda tokens: list(
                filter(lambda token: len(token.value) >= self.word_min_length, tokens)
            )
        )

    def _make_set(self, series: pd.Series) -> pd.Series:
        return series.apply(lambda tokens: set(tokens))

    def preprocess(self, series: pd.Series) -> pd.Series:
        if self.word_min_length:
            series = self._filter(series)
        series = self._make_set(series)

        return series
