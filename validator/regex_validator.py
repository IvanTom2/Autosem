import pandas as pd
import re
import numpy as np


def upload_data(
    semantic_path: str,
    validation_path: str,
) -> tuple[pd.Series, pd.Series]:
    def upload(path: str) -> pd.Series:
        if re.search(".csv$", path):
            data = pd.read_csv(path)
        else:
            data = pd.read_excel(path)
        return data

    semantic = upload(semantic_path)
    validation = upload(validation_path)
    return semantic, validation


class RegexValdator(object):
    def __init__(
        self,
        semantic: pd.DataFrame,
        validation: pd.DataFrame,
        plus_column: str = "Плюс-слова",
        minus_column: str = "Минус-слова",
        regex_column: str = "Regex",
        validate_by: str = "Строка валидации",
        semantic_merge_by: str = "Название",
        validation_merge_by: str = "Название",
    ) -> None:
        self.semantic = semantic
        self.validation = validation
        self.plus_column = plus_column
        self.minus_column = minus_column
        self.regex_column = regex_column
        self.validate_by = validate_by
        self.semantic_merge_by = semantic_merge_by
        self.validation_merge_by = validation_merge_by

    def _prepare_minus(
        self,
        data: pd.DataFrame,
        minus: str,
    ) -> pd.DataFrame:
        data["minus_rx"] = np.where(
            data[minus].isna(),
            data[minus],
            data[minus].str.replace("^\||\|$", "", regex=True),
        )
        return data

    def _validate_by_minus(
        self,
        row: pd.Series,
        validate_by: str,
    ) -> bool:
        if re.search(row["minus_rx"], row[validate_by], flags=re.IGNORECASE):
            return 0
        else:
            return 1

    def validateByMinus(
        self,
        data: pd.DataFrame,
        validate_by: str,
        minus: str,
    ) -> pd.DataFrame:
        data["_minus_valid"] = 1
        data[minus] = data[minus].replace("", np.nan)
        not_na = list(data[data[minus].notna()].index)
        if len(not_na) > 0:
            to_valid = data.iloc[not_na][[validate_by, minus]]

            to_valid = self._prepare_minus(to_valid, minus)
            data.loc[not_na, "_minus_valid"] = to_valid.apply(
                self._validate_by_minus,
                axis=1,
                args=(validate_by,),
            )

        return data

    def _prepare_plus(data: pd.DataFrame, plus: str) -> pd.DataFrame:
        data[plus] = data[plus].fillna("")
        data[plus] = data[plus].str.replace("^\||\|$", "", regex=True)
        data["plus_rx"] = data[plus].str.replace("|", "))(?=.*(")
        data["plus_rx"] = "(?=.*(" + data["plus_rx"] + "))"
        data["plus_rx"] = data["plus_rx"].replace("(?=.*())", np.nan)
        return data

    def _validate_by_plus(self, row: pd.Series, validate_by: str) -> bool:
        if re.search(row["plus_rx"], row[validate_by], flags=re.IGNORECASE):
            return 1
        else:
            return 0

    def validateByPlus(
        self,
        data: pd.DataFrame,
        validate_by: str,
        plus: str,
    ) -> pd.DataFrame:
        data["_plus_valid"] = 1
        data[plus] = data[plus].replace("", np.nan)
        not_na = list(data[data[plus].notna()].index)
        if len(not_na) > 0:
            to_valid = data.iloc[not_na][[validate_by, plus]]

            to_valid = self._prepare_plus(to_valid, plus)
            data.loc[not_na, "_plus_valid"] = to_valid.apply(
                self._validate_by_plus,
                axis=1,
                args=(validate_by,),
            )

        return data

    def _validate_by_regex(
        self,
        row: pd.Series,
        validate_by: str,
        regex: str,
    ) -> bool:
        if re.match(row[regex], row[validate_by], flags=re.IGNORECASE):
            return 1
        else:
            return 0

    def validateByRegex(
        self,
        data: pd.DataFrame,
        validate_by: str,
        regex: str,
    ) -> pd.DataFrame:
        data["_regex_valid"] = 1
        data[regex] = data[regex].replace("", np.nan)
        not_na = list(data[data[regex].notna()].index)
        if len(not_na) > 0:
            to_valid = data.iloc[not_na][[validate_by, regex]]
            data.loc[not_na, "_regex_valid"] = to_valid.apply(
                self._validate_by_regex,
                axis=1,
                args=(validate_by, regex),
            )

        return data

    def _merge_data(self) -> pd.DataFrame:
        val_data = self.validation.merge(
            self.semantic[
                [
                    self.semantic_merge_by,
                    self.plus_column,
                    self.minus_column,
                    self.regex_column,
                ]
            ],
            how="left",
            left_on=self.semantic_merge_by,
            right_on=self.validation_merge_by,
        )
        val_data.index = range(len(val_data))
        return val_data

    def validate(self):
        val_data = self._merge_data()

        val_data = self.validateByMinus(val_data, self.validate_by, self.minus_column)
        val_data = self.validateByPlus(val_data, self.validate_by, self.plus_column)
        val_data = self.validateByRegex(val_data, self.validate_by, self.regex_column)

        val_data["valid"] = val_data[
            ["_minus_valid", "_plus_valid", "_regex_valid"]
        ].sum(axis=1)
        return val_data


if __name__ == "__main__":
    semantic, validation = upload_data(
        semantic_path=r"C:\Users\tomilov-iv\Desktop\BrandPol\validator\CommonSem.xlsx",
        validation_path=r"C:\Users\tomilov-iv\Desktop\BrandPol\validator\Links.xlsx",
    )

    regex_validator = RegexValdator()
    validation = regex_validator(semantic, validation, validate_by="Строка валидации")
    print(validation)

    # validation.to_excel('validated.xlsx', index=False)
