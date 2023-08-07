import math

from tokenization import *
from preprocessing import *
from fuzzy_search import *
from ratio import *


def rate_func(value: float) -> float:
    return value


class FuzzyJakkarValidator(object):
    def __init__(
        self,
        tokenizer: AbstractTokenizer,
        preprocessor: AbstractPreprocessor,
        fuzzy_searcher: AbstractFuzzySearcher,
        rate_counter: AbstactRateCounter,
        marks_counter: AbstractMarksCounter,
        symbols_to_del: str = "'\"/",
        delete_rx: bool = False,
        word_min_length: int = 3,
        fuzzy_threshold: int = 65,
        count_mark_by: str = "union",
        multiple_marks: bool = False,
        save_ratio: bool = False,
    ):
        self.tokenizer = tokenizer
        self.preprocessor = preprocessor
        self.fuzzy_searcher = fuzzy_searcher
        self.rate_counter = rate_counter
        self.marks_counter = marks_counter

        self.delete_rx = delete_rx
        self.symbols_to_del = symbols_to_del
        self.word_min_length = word_min_length
        self.fuzzy_threshold = fuzzy_threshold
        self.count_mark_by = count_mark_by
        self.multiple_marks = multiple_marks
        self.save_ratio = save_ratio

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

    def _delete_symbols(self, series: pd.Series):
        symbols_to_del = "|".join(list(self.symbols_to_del))
        series = series.str.replace(symbols_to_del, "", regex=True)
        return series

    def _create_working_rows(
        self,
        validation: pd.DataFrame,
        client_column: str,
        site_column: str,
    ) -> pd.DataFrame:
        validation["_client"] = self._delete_symbols(validation[client_column])
        validation["_site"] = self._delete_symbols(validation[site_column])
        return validation

    def _tokenize(
        self, data: pd.DataFrame, col: str, token_col_name: str
    ) -> pd.DataFrame:
        data = self.tokenizer.tokenize(data, col, token_col_name)
        return data

    def process_tokenization(self, validation: pd.DataFrame) -> pd.DataFrame:
        self._progress_ind("client_tokens")
        validation = self._tokenize(validation, "_client", "ctokens")

        self._progress_ind("site_tokens")
        validation = self._tokenize(validation, "_site", "stokens")

        return validation

    def process_preprocessing(self, validation: pd.DataFrame) -> pd.DataFrame:
        validation["ctokens"] = self.preprocessor.preprocess(validation["ctokens"])
        validation["stokens"] = self.preprocessor.preprocess(validation["stokens"])
        return validation

    def process_fuzzy_similarity(self, validation: pd.DataFrame) -> None:
        # tokens contain similar tokens
        uniq_tokens = fuzzy_searcher.search(
            validation["ctokens"],
            validation["stokens"],
        )
        return uniq_tokens

    def process_ratio(self, validation: pd.DataFrame, uniq_tokens: set) -> dict:
        ratio = self.rate_counter.count_ratio(
            validation["ctokens"],
            validation["stokens"],
            uniq_tokens,
        )

        return ratio

    def process_marks_counting(
        self,
        validation: pd.DataFrame,
    ) -> pd.DataFrame:
        return self.marks_counter.count_marks(
            self.ratio,
            validation,
            "ctokens",
            "stokens",
        )

    def _delete_working_rows(self, validation: pd.DataFrame) -> pd.DataFrame:
        self._progress_ind("end")
        validation.drop(["_client", "_site"], axis=1, inplace=True)
        # validation.drop(["ctokens", "stokens"], axis=1, inplace=True)
        return validation

    def validate(
        self,
        validation: pd.DataFrame,
        client_column: str = "Название",
        site_column: str = "Строка валидации",
    ) -> pd.DataFrame:
        validation = self._create_working_rows(
            validation,
            client_column,
            site_column,
        )

        if self.delete_rx:
            self._progress_ind("delete_rx")

        validation = self.process_tokenization(validation)
        validation = self.process_preprocessing(validation)

        uniq_tokens = self.process_fuzzy_similarity(validation)
        self.ratio = self.process_ratio(validation, uniq_tokens)

        # self._save_ratio()

        validation = self.process_marks_counting(validation)
        validation = self._delete_working_rows(validation)
        return validation


if __name__ == "__main__":
    data = pd.read_excel(
        r"C:\Users\tomilov-iv\Desktop\BrandPol\jakkar_validator\test_data.xlsx"
    )

    index = indexer()
    weights_rules = RegexCustomWeights(caps=1, capital=1, low=1, other=1, symbols="")

    tokenizer = RegexTokenizer(
        {
            "english": 1,
            "russian": 1,
        },
        weights_rules=weights_rules,
    )

    preprocessor = Preprocessor(word_min_length=3)
    fuzzy_searcher = FuzzySearcher(fuzzy_threshold=65)
    rate_counter = RateCounter(rate_function=rate_func)
    marks_counter = MarksCounter(multiple_marks=True)

    validator = FuzzyJakkarValidator(
        tokenizer=tokenizer,
        preprocessor=preprocessor,
        fuzzy_searcher=fuzzy_searcher,
        rate_counter=rate_counter,
        marks_counter=marks_counter,
    )

    result = validator.validate(data, "Название клиент", "Название сайт")
    result.to_excel("result.xlsx", index=0)
