import pandas as pd
import numpy as np
import sys
import os


sys.path.append(os.path.dirname(os.path.dirname(__file__)))


from autosem.word_extraction import *
from autosem.measures_extraction import *
from autosem.counts_extraction import *
from autosem.cross_semantic import *
from util import upload, save


if __name__ == "__main__":
    ru = LanguageRules(
        "russian",
        symbols="",
        with_numbers=True,
        check_letters=True,
        startUpper=False,
        min_lenght=3,
        max_words=2,
        stemming=True,
    )

    eng = LanguageRules(
        "english",
        symbols="",
        with_numbers=True,
        check_letters=True,
        startUpper=False,
        min_lenght=3,
        max_words=2,
        stemming=True,
    )

    ruExtr = WordsExtractor(ru, expand_spaces=True)
    engExtr = WordsExtractor(eng, expand_spaces=True)

    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\BrandPol\add0108.xlsx")
    data = ruExtr.extract(data, "Название клиента")
    data = engExtr.extract(data, "Название клиента")

    data.to_excel("newbies_news.xlsx")
