from sqlalchemy.orm import Mapped
from pydantic import BaseModel


class ProductBase(BaseModel):

    name: str
    description: str
    price: int


class Product(ProductBase):
    id: int


class ProductCreate(BaseModel):
    ...