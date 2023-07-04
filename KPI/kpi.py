import math
from scipy import stats


def confidence_interval(sign, p, n):
    t_value = stats.t.ppf(1 - (sign / 2), n)
    dev = t_value * math.sqrt(p * (1 - p) / n)

    conf_bot = p - dev
    conf_top = p + dev
    return conf_bot, conf_top


if __name__ == "__main__":
    significance = 0.05
    p = 0.2
    n = 50

    conf = confidence_interval(significance, p, n)[1]
    print(conf)
