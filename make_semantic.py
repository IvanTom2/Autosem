import pandas as pd
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
        symbols="'",
        startUpper=False,
        check_letters=False,
        min_lenght=3,
        max_words=1,
        stemming=False,
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

    weight = MeasureExtractor(MD.mass, mode="triplet", max_values=1)
    volume = MeasureExtractor(MD.liquid, mode="triplet", max_values=1)
    conc = MeasureExtractor(MD.concByMilliliter, mode="triplet", max_values=1)
    ME = MeasureExtractor(MD.ME, mode="triplet", max_values=1)

    # ruExtr = WordsExtractor(ru, expand_spaces=True)
    engExtr = WordsExtractor(eng, expand_spaces=True)
    cross = CrosserPro([ru_cross, eng_cross], process_nearest=50)
    counts = CountsNoExtractor(excludeRX=True, NO="\sn|№|[xх]", counts="шт|пач|уп")

    # data = upload("farmaimpex.xlsx")
    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\Autosem\semantic.xlsx")
    data["name"] = data["name"] + "  "

    data = counts.extract(data, "name")
    data = weight.extract(data, "name")
    data = volume.extract(data, "name")
    data = conc.extract(data, "name")
    data = ME.extract(data, "name")

    data = concat_rx(data)
    data = cross.extract(data, "name")

    data["name"] = data["name"].str.strip()

    # save(data, "farmaimpex.xlsx")
    data.to_excel(r"zdravcity.xlsx", index=False)
