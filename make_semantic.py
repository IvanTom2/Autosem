import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(__file__) + r"\autosem")

from autosem.word_extraction import *
from autosem.measures_extraction import *
from autosem.counts_extraction import *
from autosem.cross_semantic import *
from util import concat_rx, upload, save


if __name__ == "__main__":
    MD = MeasuresData()

    ru = LanguageRules(
        "russian",
        symbols="",
        check_letters=True,
        startUpper=True,
        min_lenght=3,
        max_words=1,
        stemming=True,
    )

    eng = LanguageRules(
        "english",
        symbols="",
        startUpper=True,
        check_letters=True,
        min_lenght=3,
        max_words=1,
        stemming=True,
    )

    ru_cross = LanguageRules(
        "russian",
        symbols="",
        check_letters=True,
        min_lenght=2,
        stemming=True,
    )

    eng_cross = LanguageRules(
        "english",
        symbols="",
        check_letters=True,
        min_lenght=2,
        stemming=True,
    )

    mass = MeasureExtractor(MD.mass, mode="triplet", max_values=1)
    liquid = MeasureExtractor(MD.liquid, mode="triplet", max_values=1)
    ME = MeasureExtractor(MD.ME, mode="triplet", max_values=1)
    concMl = MeasureExtractor(
        MD.concByMilliliter,
        mode="overall",
        max_values=1,
    )

    ruExtr = WordsExtractor(ru, expand_spaces=True)
    engExtr = WordsExtractor(eng, expand_spaces=True)
    cross = CrosserPro([ru_cross, eng_cross])
    counts = CountsNoExtractor(excludeRX=True)

    # data = upload("farmaimpex.xlsx")
    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\BrandPol\semantic_txt.xlsx")
    data = ruExtr.extract(data, "Название")
    data = engExtr.extract(data, "Название")
    data = counts.extract(data, "Название")

    data = mass.extract(data, "Название")
    data = liquid.extract(data, "Название")
    data = ME.extract(data, "Название")
    data = concMl.extract(data, "Название")

    data = concat_rx(data)
    # data = cross.extract(data, "Название")

    # save(data, "farmaimpex.xlsx")
    data.to_excel(r"C:\Users\tomilov-iv\Desktop\BrandPol\katren_sem.xlsx", index=False)
