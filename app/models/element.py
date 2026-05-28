from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Element(Base):
    __tablename__ = "elements"

    id: Mapped[int] = mapped_column(primary_key=True)

    symbol: Mapped[str] = mapped_column(String(10), unique=True, index=True)

    name: Mapped[str] = mapped_column(String(50))

    atomic_number: Mapped[int] = mapped_column(Integer)

    category: Mapped[str | None] = mapped_column(String(50), nullable=True)