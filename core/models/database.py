from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, declared_attr

# для унификации часть полей можно разместить в базовом абстрактном классе. И эта таблица не будет в БД
# declared_attr - это свойство, которое будет выполняться в классе на уровне `proparty`


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True)
