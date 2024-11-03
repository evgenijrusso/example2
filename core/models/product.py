from __future__ import annotations

# Константа TYPE_CHECKING всегда имеет значение False во время выполнения,
# поэтому импорт не будет оценен, но mypy (и другие инструменты проверки типов) оценят содержимое этого блока.
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, relationship

if TYPE_CHECKING:
    from . import Order
    from .order_product_association import OrderProductAssociation

from .database import Base


class Product(Base):
    # __tablename__ = "products" #  убрал название таблицы. Оно реализуется через `Base` (database)

    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
    # orders: Mapped[list[Order]] = relationship(
    #     secondary="order_product_association",
    #     back_populates="products",
    # )
    # association between Parent -> Association -> Child
    orders_details: Mapped[list[OrderProductAssociation]] = relationship(
        back_populates="product"
    )
