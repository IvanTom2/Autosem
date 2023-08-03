import pandas as pd

if __name__ == "__main__":
    semantic = pd.read_excel(
        r"C:\Users\tomilov-iv\Desktop\ReadTown\NeKnigi\Rework v2\semantic\TextSearch\_Text_v3.xlsx"
    )
    validation = pd.read_excel(
        r"C:\Users\tomilov-iv\Desktop\ReadTown\NeKnigi\Rework v2\validation\validation_text_v2_p1.xlsx"
    )

    sem_columns = [
        "Поисковый запрос",
        "Название",
        "Название клиента",
        "Ссылка на фото",
        "type",
    ]

    merged = pd.merge(
        validation,
        semantic[sem_columns],
        how="left",
        left_on="Запрос",
        right_on="Поисковый запрос",
    )

    merged.to_csv("merged.csv", sep=";")
