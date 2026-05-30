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

    material_a_risk_score: float
    material_b_risk_score: float

    winner_material_id: int
    winner_formula: str

    score_difference: float
    reasons: list[str]