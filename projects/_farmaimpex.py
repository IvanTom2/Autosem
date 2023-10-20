from template import *


if __name__ == "__main__":
    data = upload("farmaimpex.xlsx")

    ru = LanguageRules(
        "russian",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
        symbols="",
        max_words=1,
    )

    ru_cross = LanguageRules(
        "russian",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
        symbols="",
    )

    eng_cross = LanguageRules(
        "english",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
        symbols="",
    )

    MD = MeasuresData()
    crosser = CrosserPro([ru_cross, eng_cross])

    counts = CountsNoExtractor(counts="шт|уп|доз|пак", NO="x|n|№", excludeRX=True)
    mass = MeasureExtractor(MD.mass, mode="triplet", max_values=1)
    liquid = MeasureExtractor(MD.liquid, mode="overall", max_values=1)
    ME = MeasureExtractor(MD.ME, mode="triplet", max_values=1)
    concMl = MeasureExtractor(MD.concByMilliliter, mode="overall", max_values=1)

    data = counts.extract(data, "Название")
    data = mass.extract(data, "Название")
    data = liquid.extract(data, "Название")
    data = ME.extract(data, "Название")
    data = concMl.extract(data, "Название")

    words_extractor = WordsExtractor(ru, expand_spaces=True)
    ru_words = words_extractor.extract(data, "Название", "series")

    weights_value_extractor = ValuesExtractorByRx(MD.mass, 1)
    counts_value_extractor = ValuesExtractorByRx("Количество (№)", 1)

    weights_values = weights_value_extractor.extract(data, "Название")
    counts_values = counts_value_extractor.extract(data, "Название")

    data["Поисковой запрос"] = ru_words + " " + weights_values + " " + counts_values

    data = concat_rx(data)
    data = crosser.extract(data, "Название")

    save(data, "farmaimpex_out.xlsx")
