from pydantic import BaseModel


class SensitivityAnalysisRequest(BaseModel):
    material_id: int


class SensitivityScenarioResult(BaseModel):
    scenario: str
    adjusted_score: float
    score_delta: float


class SensitivityAnalysisResult(BaseModel):
    material_id: int
    formula: str
    baseline_score: float
    baseline_material_risk_score: float
    sensitivity_level: str
    scenarios: list[SensitivityScenarioResult]