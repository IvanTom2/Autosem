from template import *


if __name__ == "__main__":
    MD = MeasuresData()
    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\Autosem\basic_semantic.xlsx")

    NAME = "Название клиента"

    ru = LanguageRules(
        "russian",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        max_words=2,
        stemming=False,
        joiner=" ",
    )

    eng = LanguageRules(
        "english",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        max_words=2,
        stemming=False,
        joiner=" ",
    )

    ru_cross = LanguageRules(
        "russian",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
    )

    eng_cross = LanguageRules(
        "english",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
    )

    crosser = CrosserPro([ru_cross, eng_cross], process_nearest=100)

    ru_extr = WordsExtractor(ru, expand_spaces=True)
    eng_extr = WordsExtractor(eng, expand_spaces=True)

    counts = CountsNoExtractor(counts="шт|уп|доз|пак", NO="[xх]|\sn|№", excludeRX=True)
    mass = MeasureExtractor(MD.mass, mode="triplet", max_values=1)
    liquid = MeasureExtractor(MD.liquid, mode="overall", max_values=1)
    ME = MeasureExtractor(MD.ME, mode="triplet", max_values=1)
    concMl = MeasureExtractor(MD.concByMilliliter, mode="overall", max_values=1)

    data = counts.extract(data, NAME)
    data = mass.extract(data, NAME)
    data = liquid.extract(data, NAME)
    data = ME.extract(data, NAME)
    data = concMl.extract(data, NAME)

    ru_words = ru_extr.extract(data, NAME, "series")
    eng_words = eng_extr.extract(data, NAME, "series")

    data["query"] = ru_words + " " + eng_words

    data = concat_rx(data)
    data = crosser.extract(data, NAME)

    data.to_excel("katren_sem.xlsx", index=False)
