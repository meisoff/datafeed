import json
from operator import itemgetter
from sqlalchemy.orm import Session
import json

import pedantic_models, database

def create_product(product: pedantic_models.Item):
    database.Product.create(**product.dict())

def get_products(limit: int = 100):
    products = []
    for product in database.Product.select().order_by(database.Product.price.desc()).dicts().execute():
        products.append(product)
    return products

def delete_product(id: int):
    database.Product.delete_by_id(id)

def add_many_items(items: list):
    database.Product.insert_many(items).execute()