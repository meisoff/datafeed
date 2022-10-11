import json
from operator import itemgetter
from sqlalchemy.orm import Session
import json

from . import models, schemas


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.Item):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_items(db: Session):
    db.query(models.Item).delete()
    db.commit()

def get_laptop_by_brand(db: Session, brandName: str):
    return db.query(models.Item).filter(models.Item.brandName == brandName).all()

def add_items_from_file(db: Session):
    with open('/home/daniil/Projects/angry_top_repo/src/base.json', 'r', encoding='utf-8') as fh:
        data = json.load(fh)
        
        for i in range(len(data)):
            item = models.Item()
            item.id = data[i]['id'] 
            item.brandName = data[i]['brandName'] 
            item.categoryId = data[i]['categoryId'] 
            item.categoryName = data[i]['categoryName'] 
            item.shortName = data[i]['shortName'] 
            item.oldPrice = data[i]['oldPrice'] 
            item.price = data[i]['price'] 
            item.clubPrice = data[i]['clubPrice'] 
            db.add(item)
            db.commit()
            db.refresh(item)
