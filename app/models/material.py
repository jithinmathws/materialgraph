from sqlalchemy import Boolean, Float, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Material(Base):
    __tablename__ = "materials"

    id: Mapped[int] = mapped_column(primary_key=True)

    mp_id: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    formula: Mapped[str] = mapped_column(String(100))
    pretty_formula: Mapped[str] = mapped_column(String(100))

    material_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    band_gap: Mapped[float | None] = mapped_column(Float, nullable=True)
    energy_above_hull: Mapped[float | None] = mapped_column(Float, nullable=True)
    formation_energy_per_atom: Mapped[float | None] = mapped_column(Float, nullable=True)
    density: Mapped[float | None] = mapped_column(Float, nullable=True)

    is_stable: Mapped[bool] = mapped_column(Boolean, default=False)

    source: Mapped[str] = mapped_column(String(100), default="materials_project")
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)