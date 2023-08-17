import pandas as pd
import sys
import os

sys.path.append(os.path.dirname(__file__) + r"\autosem")

from autosem.word_extraction import *
from autosem.measures_extraction import *
from autosem.counts_extraction import *
from autosem.cross_semantic import *
from util import save, upload, concat_rx


if __name__ == '__main__':
    data = pd.read_excel(r'C:\Users\tomilov-iv\Desktop\BrandPol\SKU_new.xlsx')

    eng = LanguageRules(
        "english",
        check_letters=False,
        with_numbers=True,
        min_lenght=0,
        stemming=False,
        symbols="-",
    )

    crosser = CrosserPro(
        [eng], delete_rx=False,
    )

    data = crosser.extract(data, "Артикул")
    data.to_excel('river.xlsx', index=False)
