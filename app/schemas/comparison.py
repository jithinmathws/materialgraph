from typing import Literal

from pydantic import BaseModel, Field


class CandidateComparisonRequest(BaseModel):
    material_a_id: int
    material_b_id: int
    scarce_elements: list[str] = Field(default_factory=list)
    avoid_elements: list[str] = Field(default_factory=list)
    require_stable: bool = True
    max_energy_above_hull: float | None = 0.05


class CandidateComparisonResult(BaseModel):
    material_a_id: int
    material_b_id: int

    material_a_formula: str
    material_b_formula: str

    material_a_score: float
    material_b_score: float

    material_a_risk_score: float | None = None
    material_b_risk_score: float | None = None

    comparison_type: Literal["winner", "tie"]

    # Backward-compatible singular winner fields.
    # These are None when both candidates have equal scores.
    winner_material_id: int | None = None
    winner_formula: str | None = None

    tied_material_ids: list[int] = Field(default_factory=list)
    tied_formulas: list[str] = Field(default_factory=list)

    score_difference: float
    reasons: list[str]