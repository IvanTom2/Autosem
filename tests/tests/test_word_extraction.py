"""
Don't have enough time to write enough pytests
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from autosem.autosem_funcs.word_extraction_funcs import *
from data_for_tests import *


def test_extract_words_english():
    testdata = data_for_extract_words_english()
    data = pd.DataFrame(
        data=[
            "Hello this is Test",
            "hello world it is beautiful. CH2O5NH",
            "Who is the most high-skilled player in NBA?",
        ],
        columns=["Название"],
    )

    startupper = extractWords(
        data["Название"],
        startUpper=True,
        language="english",
        symbols="-",
        word_boundary=True,
    )

    noncase = extractWords(
        data["Название"],
        startUpper=False,
        language="english",
        symbols="-",
        word_boundary=True,
    )

    onlyupper = extractWords(
        data["Название"],
        onlyUpper=True,
        language="english",
        symbols="-",
        word_boundary=True,
    )

    # printTestData(startupper)
    # printTestData(noncase)
    # printTestData(onlyupper)

    checkout(
        {
            "startupper": startupper,
            "noncase": noncase,
            "onlyupper": onlyupper,
        },
        testdata,
    )


def test_extract_words_russian():
    testdata = data_for_extract_words_russian()
    data = pd.DataFrame(
        data=[
            "Привет это просто Тест",
            "привет мир! это прекрасно)",
            "Кто самый-самый скилловый игрок в НБА?",
        ],
        columns=["Название"],
    )

    startupper = extractWords(
        data["Название"],
        startUpper=True,
        language="russian",
        symbols="-",
        word_boundary=True,
    )

    noncase = extractWords(
        data["Название"],
        startUpper=False,
        language="russian",
        symbols="-",
        word_boundary=True,
    )

    onlyupper = extractWords(
        data["Название"],
        onlyUpper=True,
        language="russian",
        symbols="-",
        word_boundary=True,
    )

    # printTestData(startupper)
    # printTestData(noncase)
    # printTestData(onlyupper)

    checkout(
        {
            "startupper": startupper,
            "noncase": noncase,
            "onlyupper": onlyupper,
        },
        testdata,
    )


def test_extract_words_symbols():
    testdata = data_for_extract_words_check_symbols()
    data = pd.DataFrame(
        data=[
            "Hello! It's symbols test. Hate/no hate it, but i get money$$$",
        ],
        columns=["Название"],
    )

    symbols = extractWords(
        data["Название"],
        symbols="/",
    )

    # printTestData(symbols)

    checkout({"symbols": symbols}, testdata)


def test_extract_words_word_boundary():
    testdata = data_for_extract_words_check_word_boundary()
    data = pd.DataFrame(
        data=[
            "Word1, word2, word3 word 4",
        ],
        columns=["Название"],
    )

    with_wb = extractWords(data["Название"], word_boundary=True)
    without_wb = extractWords(data["Название"])

    # printTestData(with_wb)
    # printTestData(without_wb)

    checkout({"with_wb": with_wb, "without_wb": without_wb}, testdata)


if __name__ == "__main__":
    test_extract_words_english()
    # test_extract_words_russian()
    # test_extract_words_symbols()
    # test_extract_words_word_boundary()
