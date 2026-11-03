
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class Pet(Base):
    __tablename__ = "pets"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(60)
    )

    hunger: Mapped[int] = mapped_column(
        Integer,
        default=50
    )
