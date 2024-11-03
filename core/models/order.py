from __future__ import annotations

# для удобства. Тогда можно указать без кавычек [Product]

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import func

from .database import Base


if TYPE_CHECKING:
    from .product import Product
    from .order_product_association import OrderProductAssociation


class Order(Base):
    promocode: Mapped[str | None]
    create_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        default=datetime.now(timezone.utc),  # в оригинале - datetime.utcnow
    )
    # products: Mapped[list[Product]] = relationship(
    #     secondary="order_product_association",
    #     back_populates="orders",
    # )
    # association between Parent -> Association -> Child
    products_details: Mapped[list[OrderProductAssociation]] = relationship(
        back_populates="order"
    )
