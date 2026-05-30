from pydantic import BaseModel


class ElementRiskSummary(BaseModel):
    symbol: str
    risk_score: float
    supply_risk_score: float | None = None
    geopolitical_risk_score: float | None = None
    toxicity_score: float | None = None


class MaterialRiskRead(BaseModel):
    material_id: int
    formula: str
    pretty_formula: str
    material_risk_score: float
    element_risks: list[ElementRiskSummary]