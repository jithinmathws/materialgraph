from pydantic import BaseModel, ConfigDict

from app.schemas.material_common import MaterialRiskSummary, MaterialRelationshipSummary


class MaterialRecommendationRead(MaterialRiskSummary, MaterialRelationshipSummary):
    similarity_score: float
    criticality_delta: float | None
    criticality_direction: str
    recommendation_score: float
    recommendation_reason: str


class MaterialRecommendationResponse(MaterialRiskSummary):
    model_config = ConfigDict(from_attributes=True)

    recommendations: list[MaterialRecommendationRead]


class MaterialScenarioRead(MaterialRecommendationRead):
    scenario_score: float
    scenario_delta: float
    scenario_reason: str


class MaterialRecommendationScenario(BaseModel):
    element: str
    supply_risk_multiplier: float
    avoid_element: str | None = None
    prefer_element: str | None = None
    limit: int


class MaterialScenarioRecommendationResponse(MaterialRiskSummary):
    model_config = ConfigDict(from_attributes=True)

    scenario: MaterialRecommendationScenario
    recommendations: list[MaterialScenarioRead]