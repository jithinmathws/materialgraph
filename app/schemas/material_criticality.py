from pydantic import BaseModel, ConfigDict


class MaterialCriticalityElement(BaseModel):
    element_id: int
    symbol: str
    name: str

    fraction: float
    risk_year: int | None

    abundance_score: float | None
    supply_risk_score: float | None
    toxicity_score: float | None
    recyclability_score: float | None
    geopolitical_risk_score: float | None

    element_criticality_score: float


class MaterialCriticalityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    mp_id: str | None
    pretty_formula: str | None
    formula: str | None

    criticality_score: float | None

    elements: list[MaterialCriticalityElement]