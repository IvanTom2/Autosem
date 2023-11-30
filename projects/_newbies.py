from template import *


if __name__ == "__main__":
    # data = upload("newbies.xlsx")
    data = pd.read_excel(r"C:\Users\tomilov-iv\Desktop\Autosem\add2211.xlsx")

    ru = LanguageRules(
        "russian",
        symbols="",
        with_numbers=True,
        check_letters=True,
        startUpper=False,
        min_lenght=3,
        max_words=2,
        stemming=True,
    )

    eng = LanguageRules(
        "english",
        symbols="",
        with_numbers=True,
        check_letters=True,
        startUpper=False,
        min_lenght=3,
        max_words=2,
        stemming=True,
    )

    ruExtr = WordsExtractor(ru, expand_spaces=True)
    engExtr = WordsExtractor(eng, expand_spaces=True)

    data = ruExtr.extract(data, "Название клиента")
    data = engExtr.extract(data, "Название клиента")

    # save(data, "newbies_out.xlsx")
    data.to_excel("newbies.xlsx", index=False)
