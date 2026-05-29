from sqlalchemy import Float, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ElementRiskProfile(Base):
    __tablename__ = "element_risk_profiles"

    id: Mapped[int] = mapped_column(primary_key=True)

    element_id: Mapped[int] = mapped_column(
        ForeignKey("elements.id", ondelete="CASCADE"),
        index=True,
    )

    year: Mapped[int] = mapped_column(Integer)

    abundance_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    supply_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    toxicity_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    recyclability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    geopolitical_risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    source: Mapped[str] = mapped_column(String(100), default="usgs")

    __table_args__ = (
        UniqueConstraint("element_id", "year", name="uq_element_risk_profile_year"),
    )