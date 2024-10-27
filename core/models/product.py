from sqlalchemy.orm import Mapped

from .database import Base


class Product(Base):
    # __tablename__ = "products" #  убрал название таблицы. Оно реализуется через `Base` (database)

    name: Mapped[str]
    description: Mapped[str]
    price: Mapped[int]
