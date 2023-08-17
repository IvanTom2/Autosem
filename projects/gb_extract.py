import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from autosem.word_extraction import *
from autosem.measures_extraction import *
from autosem.counts_extraction import *
from autosem.cross_semantic import *
from util import save, upload, concat_rx


if __name__ == "__main__":
    data = pd.read_excel("ivan.xlsx")

    MD = MeasuresData()
    mass = MeasureExtractor(MD.memory)

    data = mass.extract(data, "Название")
    data = concat_rx(data)

    data.to_excel("yan.xlsx", index=False)
