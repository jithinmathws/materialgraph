from pydantic import BaseModel, ConfigDict


class ElementRiskProfileRead(BaseModel):
    id: int
    element_id: int
    year: int
    abundance_score: float | None = None
    supply_risk_score: float | None = None
    toxicity_score: float | None = None
    recyclability_score: float | None = None
    geopolitical_risk_score: float | None = None
    source: str

    model_config = ConfigDict(from_attributes=True)