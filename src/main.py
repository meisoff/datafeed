from operator import itemgetter
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
import pandas as pd

from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/create_items/", response_model=schemas.Item)
def create_item_for_user(
    item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

@app.get("/items/delete_all/")
def delete_all_items(db: Session = Depends(get_db)):
    crud.delete_items(db)

@app.get("/add_items_to_db_from_json/")
def add_items_to_db_from_json(db: Session = Depends(get_db)):
    crud.add_items_from_file(db=db)     

@app.get("/laptops/{brandName}/price/average/")
def get_laptop_avegare_price(brandName: str, db: Session = Depends(get_db)):
    items = crud.get_laptop_by_brand(db=db, brandName=brandName)
    prices = []
    
    for item in items:
        prices.append(item.price)
    
    df_prices = pd.DataFrame(prices)
    return df_prices.mean()
    
