from template import *


if __name__ == "__main__":
    MD = MeasuresData()
    NAME = "Название клиента"

    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\Autosem\basic_semantic.xlsx")
    data[NAME] = data[NAME] + "  "

    ru_cross = LanguageRules(
        "russian",
        symbols="",
        check_letters=True,
        min_lenght=2,
        stemming=True,
    )

    eng_cross = LanguageRules(
        "english",
        symbols="",
        check_letters=True,
        min_lenght=2,
        stemming=True,
    )

    weight = MeasureExtractor(MD.mass, mode="triplet", max_values=1)
    volume = MeasureExtractor(MD.liquid, mode="triplet", max_values=1)
    conc = MeasureExtractor(MD.concByMilliliter, mode="triplet", max_values=1)
    ME = MeasureExtractor(MD.ME, mode="triplet", max_values=1)

    cross = CrosserPro([ru_cross, eng_cross], process_nearest=50)
    counts = CountsNoExtractor(excludeRX=True, NO="\sn|№|[xх]", counts="шт|пач|уп")

    data = counts.extract(data, NAME)
    data = weight.extract(data, NAME)
    data = volume.extract(data, NAME)
    data = conc.extract(data, NAME)
    data = ME.extract(data, NAME)

    data = concat_rx(data)
    data = cross.extract(data, NAME)

    data[NAME] = data[NAME].str.strip()

    data.to_excel("zdravcity.xlsx", index=False)
