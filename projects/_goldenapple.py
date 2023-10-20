from template import *


if __name__ == "__main__":
    data = upload("goldapp.xlsx")

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

    save(data, "goldapp_out.xlsx")
