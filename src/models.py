from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class Item(Base):
    __tablename__ = "items"

    id_counter = Column(Integer, primary_key=True, index=True)
    id = Column(Integer)
    brandName = Column(String)
    shortName = Column(String)
    categoryId = Column(Integer)
    categoryName = Column(String)
    price = Column(Integer)
    oldPrice = Column(Integer)
    clubPrice = Column(Integer)

    # items = relationship("Item")