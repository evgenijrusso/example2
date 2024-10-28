# from typing import TYPE_CHECKING
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
from .mixins import UserRelationMixin

# if TYPE_CHECKING:
#     from .user import User


class Post(UserRelationMixin, Base):
    _user_back_populated = "posts"

    title: Mapped[str] = mapped_column(String(100), unique=False)
    body: Mapped[str] = mapped_column(Text, default="", server_default="")


#  user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)   # эти поля используются в mixins
#  user: Mapped["User"] = relationship(back_populates="posts")
