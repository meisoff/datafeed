import pandas as pd
import crud
import os, inspect, sys

def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)


path = os.path.join(get_script_dir(), 'raduga.xlsx')
df = pd.read_excel(path)

ozon_index = [df.columns.get_loc(i) for i in df.columns if "www.ozon.ru" in i]  # Ищем колонки с значением www.ozon.ru
all_index = [df.columns.get_loc("Код"), df.columns.get_loc("Бренд"), df.columns.get_loc("Название"), df.columns.get_loc("МВЦ руб.")]  # Массив для нужных индексов, вносим первые основные

for i in ozon_index:
    all_index.extend([i, i+1, i+3])  # Добавляем найденные индексы из ozon_index, "регион" и "формула"

df = pd.DataFrame(df.drop([i for i in df.columns if df.columns.get_loc(i) not in all_index], axis=1))  # Сортируем фрейм - выкидываем ненужные столбцы
sort_ozon_index = [df.columns.get_loc(i) for i in df.columns if "www.ozon.ru" in i] # Получаем сортированные индексы колонок с www.ozon.ru

own_base = []  # Массив для основной базы
url_base = []  # Массив для связанной базы (ссылки)

for i in range(len(df)):
    # Здесь идет сохранение в базу данных
    crud.create_product({
        "index": int(df.loc[i, "Код"]),
        "brand": str(df.loc[i, "Бренд"]),
        "name": str(df.loc[i, "Название"]),
        "mpp": int(df.loc[i, "МВЦ руб."])
    })

    for j in sort_ozon_index:
        if type(df.iloc[i, j]) == str:
            crud.create_link({
                "index": int(df.loc[i, "Код"]),
                "url": str(df.iloc[i, j]),
                "region": int(df.iloc[i, j+1]),
                "formula": None if str(df.iloc[i, j+2]) == "nan" else str(df.iloc[i, j+2])
            })

# Сохраняю для проверки
# with open("./own_base.json", "w", encoding='utf-8') as f:
#     json.dump(own_base, f, ensure_ascii=False, indent=4)

# with open("./url_base.json", "w", encoding='utf-8') as f:
#     json.dump(url_base, f, ensure_ascii=False, indent=4)

