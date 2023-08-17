import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(__file__) + r"\autosem")
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from autosem.word_extraction import *
from autosem.measures_extraction import *
from autosem.counts_extraction import *
from autosem.cross_semantic import *
from util import save, upload, concat_rx


if __name__ == "__main__":
    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\BrandPol_old\НОВЫЕ.xlsx")

    ru = LanguageRules(
        "russian",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
        symbols="",
    )
    eng = LanguageRules(
        "english",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
        symbols="",
    )

    crosser = CrosserPro(
        [ru, eng],
    )
    counts = CountsNoExtractor(counts="шт|уп|доз|пак", NO="x|n|№", excludeRX=True)
    MD = MeasuresData()

    mass = MeasureExtractor(MD.mass(), mode="triplet", max_values=1)
    liquid = MeasureExtractor(MD.liquid(), mode="overall", max_values=1)
    ME = MeasureExtractor(MD.ME(), mode="triplet", max_values=1)
    concMl = MeasureExtractor(MD.concByMilliliter(), mode="overall", max_values=1)

    data = mass.extract(data, "Название")
    data = liquid.extract(data, "Название")
    data = ME.extract(data, "Название")
    data = concMl.extract(data, "Название")
    data = counts.extract(data, "Название")

    data = concat_rx(data)
    # data = crosser.extract(data, "Название")

    data.to_excel("yan.xlsx", index=False)
    # save(data, "farmaimpex.xlsx")
