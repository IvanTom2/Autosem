from dataclasses import dataclass
import pandas as pd


def checkout(extractions: dict[str, pd.Series], testdata: dict[str, list[list]]):
    for key, extraction in extractions.items():
        assert extraction.to_list() == testdata[key]


def printTestData(extraction: pd.Series):
    print(extraction.to_list())


def data_for_extract_words_english() -> dict[str, list[list]]:
    testdata = {
        "startupper": [["Hello", "Test"], [], ["Who", "NBA"]],
        "noncase": [
            ["Hello", "this", "is", "Test"],
            ["hello", "world", "it", "is", "beautiful"],
            ["Who", "is", "the", "most", "high-skilled", "player", "in", "NBA"],
        ],
        "onlyupper": [[], [], ["NBA"]],
    }
    return testdata


def data_for_extract_words_russian() -> dict[str, list[list]]:
    testdata = {
        "startupper": [["Привет", "Тест"], [], ["Кто", "НБА"]],
        "noncase": [
            ["Привет", "это", "просто", "Тест"],
            ["привет", "мир", "это", "прекрасно"],
            ["Кто", "самый-самый", "скилловый", "игрок", "в", "НБА"],
        ],
        "onlyupper": [[], [], ["НБА"]],
    }
    return testdata


def data_for_extract_words_check_symbols() -> dict[str, list[list]]:
    testdata = {
        "symbols": [
            [
                "Hello",
                "It",
                "s",
                "symbols",
                "test",
                "Hate/no",
                "hate",
                "it",
                "but",
                "i",
                "get",
                "money",
            ]
        ]
    }
    return testdata


def data_for_extract_words_check_symbols() -> dict[str, list[list]]:
    testdata = {
        "symbols": [
            [
                "Hello",
                "It",
                "s",
                "symbols",
                "test",
                "Hate/no",
                "hate",
                "it",
                "but",
                "i",
                "get",
                "money",
            ]
        ]
    }
    return testdata


def data_for_extract_words_check_word_boundary() -> dict[str, list[list]]:
    testdata = {"with_wb": [["word"]], "without_wb": [["Word", "word", "word", "word"]]}
    return testdata


if __name__ == "__main__":
    xyz = "123"
