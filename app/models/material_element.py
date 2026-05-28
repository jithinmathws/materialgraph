from sqlalchemy import ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MaterialElement(Base):
    __tablename__ = "material_elements"

    id: Mapped[int] = mapped_column(primary_key=True)

    material_id: Mapped[int] = mapped_column(
        ForeignKey("materials.id", ondelete="CASCADE")
    )

    element_id: Mapped[int] = mapped_column(
        ForeignKey("elements.id", ondelete="CASCADE")
    )

    fraction: Mapped[float] = mapped_column(Float)