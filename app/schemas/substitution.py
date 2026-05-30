from pydantic import BaseModel


class SubstitutionRequest(BaseModel):
    material_id: int
    top_n: int = 5


class SubstituteCandidate(BaseModel):
    material_id: int
    formula: str
    pretty_formula: str
    similarity_score: float
    material_risk_score: float
    rank_score: float
    shared_elements: list[str]
    replacement_elements: list[str]
    removed_elements: list[str]
    explanation: str


class SubstitutionResult(BaseModel):
    source_material_id: int
    source_formula: str
    source_risk_score: float
    substitutes: list[SubstituteCandidate]