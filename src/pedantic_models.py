from pydantic import BaseModel


class ItemBase(BaseModel):
    title: str
    price: float


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    class Config:
        orm_mode = True
