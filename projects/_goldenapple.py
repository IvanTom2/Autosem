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
    data = pd.read_excel(
        r"C:\Users\tomilov-iv\Desktop\BrandPol_old\lithuania_kaina24_sem.xlsx"
    )

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

    COLUMN = "Название клиента"

    crosser = CrosserPro(
        [ru, eng],
        process_nearest=15,
    )

    counts = CountsNoExtractor(
        counts="шт|уп|доз|пак|амп|кап|\*|x\s|х\s",
        NO="\Wx|\sх|\Wn|№|\*",
        excludeRX=True,
    )
    MD = MeasuresData()

    mass = MeasureExtractor(MD.mass, mode="triplet", max_values=1)
    liquid = MeasureExtractor(MD.liquid, mode="overall", max_values=1)
    ME = MeasureExtractor(MD.ME, mode="triplet", max_values=1)
    concMl = MeasureExtractor(MD.concByMilliliter, mode="overall", max_values=1)

    data = mass.extract(data, COLUMN)
    data = liquid.extract(data, COLUMN)
    data = ME.extract(data, COLUMN)
    data = concMl.extract(data, COLUMN)
    data = counts.extract(data, COLUMN)

    data = concat_rx(data)
    data = crosser.extract(data, COLUMN)

    data.to_excel("test_RD.xlsx", index=False)
