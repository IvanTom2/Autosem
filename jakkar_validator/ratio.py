from abc import ABC, abstractmethod
import pandas as pd
from typing import Callable

from tokenization import Token

from collections import Counter
from itertools import chain


class AbstactRateCounter(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def count_ratio(self):
        pass


class RateCounter(AbstactRateCounter):
    def __init__(
        self,
        min_ratio: float = 0,
        max_ratio: float = 1,
        uniq_max_value: int = 1,
        uniq_penalty: float = 0,
        rate_function: Callable = None,
    ) -> None:
        self.min_ratio = min_ratio
        self.max_ratio = max_ratio
        self.uniq_max_value = uniq_max_value
        self.uniq_penalty = uniq_penalty
        self.rate_function = rate_function

    def _rate_function(self, value: float) -> float:
        try:
            value = 1 / value
            if self.rate_function is not None:
                if callable(self.rate_function):
                    value = self.rate_function(value)

        except Exception as ex:
            print(ex)

        finally:
            return value

    def _uniq_penalty(self, value: int) -> float:
        value_rate = self._rate_function(value)

        value_rate = self.min_ratio if value_rate < self.min_ratio else value_rate
        value_rate = self.max_ratio if value_rate > self.max_ratio else value_rate

        if self.uniq_max_value:
            if value <= self.uniq_max_value:
                value_rate = value_rate * self.uniq_penalty

        return value_rate

    def _make_ratio(self, counts: dict) -> dict:
        ratio = {}
        for key, value in counts.items():
            rate = self._uniq_penalty(value)
            ratio[key] = rate
        return ratio

    def _process_ratio(self, tokens: list[Token]):
        tokens_values = [token.value for token in tokens]
        counts = Counter(tokens_values)

        ratio = self._make_ratio(counts)
        return ratio

    def count_ratio(
        self,
        left_tokens: pd.Series,
        right_tokens: pd.Series,
        uniq_tokens: set,
    ) -> dict:
        tokens: list[set[Token]] = left_tokens.to_list() + right_tokens.to_list()
        tokens: list[Token] = list(chain(*map(list, tokens)))

        ratio = self._process_ratio(tokens)
        return ratio


class AbstractMarksCounter(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def count_marks(self):
        pass


class MarksCounter(AbstractMarksCounter):
    def __init__(
        self,
        multiple_marks: bool = False,
        count_mark_by: str = "union",
    ) -> None:
        self.multiple_marks = multiple_marks
        self.count_mark_by = count_mark_by

    def _find_ratio(self, tokens: set[Token]):
        tokens_rates = [
            self.ratio[token.value] * token.get_custom_weight for token in tokens
        ]
        return tokens_rates

    def _try_count_mark(self, intersect: set, union: set) -> float:
        try:
            mark = intersect / sum(self._find_ratio(union))

        except Exception:
            return 0

        finally:
            return mark

    def _count_mark(
        self,
        row: pd.Series,
        left: str,
        right: str,
    ) -> float:
        intersect = row[left].intersection(row[right])

        # print([token.value for token in row["ctokens"]])
        # print([token.value for token in row["stokens"]])
        # print([token.value for token in intersect])
        # print("\n")

        if self.count_mark_by == "union":
            union = row[left].union(row[right])
        elif self.count_mark_by == "client":
            union = row[left]
        elif self.count_mark_by == "site":
            union = row[right]
        else:
            raise ValueError(
                f"There are not such choice: {self.count_mark_by}. Choices: union, client, site."
            )

        intersect = self._find_ratio(intersect)
        union = self._find_ratio(union)

        mark = self._try_count_mark(intersect, union)
        return mark

    def _count_multiple_marks(
        self,
        row: pd.Series,
        left: str,
        right: str,
    ) -> list[float]:
        intersect = row[left].intersection(row[right])

        unions = [
            row[left].union(row[right]),
            row[left],
            row[right],
        ]

        _intersect = sum(self._find_ratio(intersect))
        marks = [self._try_count_mark(_intersect, union) for union in unions]
        return marks

    def count_marks(
        self,
        ratio: dict,
        df: pd.DataFrame,
        left: str,
        right: str,
    ) -> pd.Series:
        self.ratio = ratio

        if self.multiple_marks:
            marks = df.apply(
                self._count_multiple_marks,
                axis=1,
                args=(left, right),
            )

            df["mark_union"] = marks.str[0]
            df["mark_client"] = marks.str[1]
            df["mark_site"] = marks.str[2]
        else:
            df["mark"] = df.apply(self._count_mark, axis=1, args=(left, right))

        return df
