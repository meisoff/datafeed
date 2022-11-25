import json
import pandas as pd
import database

### Работа с данными из файла ###
# Добавляет элемент в таблицу product
def create_product(product: dict):
    database.Product.create(**product)

# Добавляет элемент в таблицу links
def create_link(link: dict):
    database.Links.create(index=link['index'], link=link['url'], region=link['region'], formula=link['formula'])

### Работа с парсингом ###
# Забирает все данные, нужные для парсинга
def get_items_for_parsing():
    return database.Links.select().dicts()

# Добавляет результат парсинга
def create_result(result: dict):
    database.Results.create(index=result['index'], link=result['url'], region=result['region'], date=result['date'], price=result['price'], stock=result['stock'])

# Добавляет несколько результатов парсинга
def create_many_result(results: list):
    database.Results.insert_many(results)

### Работа с данными результирующих файлов ###
# Получить все данные из result
def get_data_for_file():
    return database.Results.select().dicts()

# Получить данные из Product
def get_from_products():
    return database.Product.select().dicts()
    
# Добавляет информацию о файле
def create_file_info(file_info: dict):
    database.FileInfo.create(date=file_info['date'], name=file_info['name'], size=file_info['size'], format=file_info['format'])

# Берет последние 5 элементов с информацией о результирующих файлах
def get_five_file_infos():
    return database.FileInfo.select().limit(5).dicts()

# Берет данные файла по индексу
def get_file_info_by_index(index: int):
    return database.FileInfo.select().where(database.FileInfo.id == index).dicts()