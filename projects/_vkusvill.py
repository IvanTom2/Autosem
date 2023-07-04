import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(__file__) + r'\autosem')

from autosem.word_extraction import *
from autosem.measures_extraction import *
from autosem.counts_extraction import *
from autosem.cross_semantic import *
from util import save, upload, concat_rx


if __name__ == '__main__':
    data = upload('vkusvill.xlsx')

    ru = LanguageRules('russian', check_letters=True, with_numbers=True, min_lenght=3, stemming=True)
    eng = LanguageRules('english', check_letters=True, with_numbers=True, min_lenght=3, stemming=True)

    crosser = CrosserPro([ru, eng], main_rule=0)
    MD = MeasuresData()

    mass = MeasureExtractor(MD.mass())
    liquid = MeasureExtractor(MD.liquid())
    percent = MeasureExtractor(MD.percentConcentration())

    data = mass.extract(data, 'Название')
    data = liquid.extract(data, 'Название')
    data = percent.extract(data, 'Название')
    data = getCountsRx(data, 'Название', counts='шт|пач|уп|бан|x|х', excludeRX=True)

    data = concat_rx(data)
    data = crosser.extract(data, 'Название')

    save(data, 'vkusvill.xlsx')
