from pydantic import BaseModel


class ItemBase(BaseModel):
    id: int
    brandName: str
    shortName: str
    categoryId: int
    categoryName: str
    price: int
    oldPrice: int
    clubPrice: int


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    class Config:
        orm_mode = True
