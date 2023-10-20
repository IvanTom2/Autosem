from template import *

if __name__ == "__main__":
    data = upload("vkusvill.xlsx")

    ru = LanguageRules(
        "russian",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
    )
    eng = LanguageRules(
        "english",
        check_letters=True,
        with_numbers=True,
        min_lenght=3,
        stemming=True,
    )

    crosser = CrosserPro([ru, eng])
    MD = MeasuresData()

    counts = CountsExtractor(counts="шт|пач|уп|бан|x|х", NO="x|n|№", excludeRX=True)
    mass = MeasureExtractor(MD.mass())
    liquid = MeasureExtractor(MD.liquid())
    percent = MeasureExtractor(MD.concPercent())

    data = mass.extract(data, "Название")
    data = liquid.extract(data, "Название")
    data = percent.extract(data, "Название")
    data = counts.extract(data, "Название", excludeRX=True)

    data = concat_rx(data)
    data = crosser.extract(data, "Название")

    save(data, "vkusvill.xlsx")
