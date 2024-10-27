from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):  # основа
    name: str
    description: str
    price: int


class Product(ProductBase):  # возвращать данные по продукту
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProductCreate(ProductBase):  # создвавать данные по продукту
    pass


class ProductUpdate(ProductCreate):
    pass


class ProductUpdatePartial(ProductCreate):
    name: str | None = None
    description: str | None = None
    price: int | None = None
