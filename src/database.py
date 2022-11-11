from peewee import *

import pedantic_models

pg_db = PostgresqlDatabase('data_feed', user='postgres', password='123',
                           host='localhost', port=5432)

class BaseModel(Model):
    class Meta:
        database = pg_db

class Product(BaseModel):
    id = IntegerField(column_name='id')
    title = TextField(column_name='title')
    price = FloatField(column_name='price')

    class Meta:
        table_name = 'product'
