from template import *
import re


def vendor_code_query():
    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\Autosem\semantic.xlsx")
    data[NAME] = data[NAME] + "  "

    data["vendor_code"] = data[NAME].apply(
        lambda x: re.findall(
            "[a-zа-я][a-zа-я0-9]{2,}-[a-zа-я0-9]{1,}",
            x,
            re.IGNORECASE,
        )
    )

    data[NAME] = data[NAME].str.strip()

    data["vendor_code"] = data["vendor_code"].apply(lambda x: "".join(x[:1]))
    data.to_excel("vencode_code_zdravcity.xlsx", index=False)


def brand_words_query():
    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\Autosem\semantic.xlsx")
    data[NAME] = data[NAME] + "  "
    data[BRAND] = data[BRAND] + "  "

    data["brand_extract"] = data[BRAND].str.replace("/", " ", regex=False)
    data["brand_extract"] += "  "
    brand = data[BRAND].apply(
        lambda x: re.findall(
            "[а-яё]{3,}",
            x,
            re.IGNORECASE,
        )
    )
    brand = brand.apply(lambda x: "".join(x[:1]))

    ru = LanguageRules(
        "russian",
        symbols="",
        check_letters=True,
        min_lenght=3,
        max_words=4,
        stemming=False,
        joiner=" ",
    )
    WE = WordsExtractor(ru, expand_spaces=True)

    words = WE.extract(data, NAME, return_mode="series")

    data["query"] = brand + " " + words

    data["query"] = data["query"].apply(lambda x: {k: "" for k in x.split(" ")}.keys())
    data["query"] = data["query"].apply(lambda x: " ".join(list(x)[:4]))

    data[NAME] = data[NAME].str.strip()
    data[BRAND] = data[BRAND].str.strip()

    data.to_excel("brand_words_zdravcity.xlsx", index=False)


if __name__ == "__main__":
    MD = MeasuresData()
    NAME = "Название клиента"
    BRAND = "Brand"

    # vendor_code_query()
    brand_words_query()
