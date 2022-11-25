from peewee import *

pg_db = PostgresqlDatabase('data_feed', user='postgres', password='123',
                           host='localhost', port=5432)

class BaseModel(Model):
    class Meta:
        database = pg_db

# Продукт, извлеченный из файла
class Product(BaseModel):
    index = IntegerField(primary_key=True, column_name='Код')
    brand = TextField(column_name='Бренд')
    name = TextField(column_name='Название')
    mpp = IntegerField(column_name='МВЦ')

    class Meta:
        table_name = 'product'

# Ссылка, извлеченная из файла
class Links(BaseModel):
    index = ForeignKeyField(Product, backref='links', column_name='Код_продукта')
    link = TextField(column_name='Ссылка')
    region = IntegerField(column_name='Регион')
    formula = TextField(null=True, column_name='Формула')

    class Meta:
        table_name = 'links'

# Результат, полученный после парсинга
class Results(BaseModel):
    index = IntegerField(column_name='Код')
    date = TextField(column_name='Дата')
    link = TextField(column_name='Ссылка')
    region = IntegerField(column_name='Регион')
    price = FloatField(null=True, column_name='Цена')
    stock = BooleanField(column_name='Наличие')

# Информация о результирующем файле
class FileInfo(BaseModel):
    date = TextField(column_name='Дата')
    name = TextField(column_name='Имя')
    size = IntegerField(column_name='Размер')
    format = TextField(column_name='Формат')