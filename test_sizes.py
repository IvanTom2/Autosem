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
    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\BrandPol\new_semantic.xlsx")

    size = SizeExtractor(basic_sep=False)

    check = size.extract(data, "Название")

    check.to_excel("check.xlsx", index=False)
