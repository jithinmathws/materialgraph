from pydantic import BaseModel, Field


class CandidateScreeningRequest(BaseModel):
    scarce_elements: list[str] = Field(default_factory=list)
    avoid_elements: list[str] = Field(default_factory=list)
    require_stable: bool = True
    max_energy_above_hull: float | None = None


class CandidateScreeningResult(BaseModel):
    material_id: int
    mp_id: str
    formula: str
    pretty_formula: str
    score: float

    material_risk_score: float | None
    risk_known: bool
    risk_profile_coverage: float
    known_risk_element_count: int
    total_element_count: int
    risk_evidence_complete: bool
    unknown_risk_elements: list[str]

    risk_penalty: float
    elements: list[str]
    contains_scarce_elements: bool
    contains_avoided_elements: bool
    reasons: list[str]