import database, crud
import os.path
import datetime

# Скрипт для создания таблиц
database.pg_db.connect()
database.pg_db.create_tables([database.Product, database.Links, database.Results, database.FileInfo])

# crud.create_file_info({
#     "date" : "23.11.2022",
#     "name" : "new_file.xlsx",
#     "size" : 321,
#     "format" : "xlsx"
# })
# crud.create_file_info({
#     "date" : "22.11.2022",
#     "name" : "raduga.xlsx",
#     "size" : 321,
#     "format" : "xlsx"
# })

# crud.create_result({
#         "index": 3,
#         "date": datetime.datetime.now(),
#         "region": 3, 
#         "url": "link",
#         "price": 123,  
#         "stock": True  
# })

# Тест загрузки данных в бд
# for i in range(3):
#     # Здесь идет сохранение, нужно добавлять сразу в базу или после добавления в массивы
#     crud.create_product({
#         "index": i,
#         "brand": 'b',
#         "name": 'n',
#         "mpp": 10
#     })

#     for j in range(3):
#         crud.create_link({
#             "index": i,
#             "url": 'l',
#             "region": j,
#             "formula": 3
#         })

# Тест извлечения данных для парсинга
# data = database.Links.select(database.Product.index, database.Product.brand, database.Links.index, database.Links.region).join(database.Product).dicts()
# for d in data:
#     print(type(d))

# data = database.Links.select().dicts()
# for d in data:
#     print(d)

# if os.path.exists("./main.py"):
#     print("True")
# else: 
#     print("False") 