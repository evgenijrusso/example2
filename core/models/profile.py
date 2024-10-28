from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
from .mixins import UserRelationMixin


class Profile(UserRelationMixin, Base):
    _user_id_unique = True
    _user_back_populated = "profile"

    first_name: Mapped[str | None] = mapped_column(String(40), unique=False)
    last_name: Mapped[str | None] = mapped_column(String(40), unique=False)
    bio: Mapped[str | None]  # без ограничения по длине
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)


#  user: Mapped["User"] = relationship(back_populates="user")
