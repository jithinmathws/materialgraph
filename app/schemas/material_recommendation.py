from pydantic import BaseModel, ConfigDict


class MaterialRecommendationRead(BaseModel):
    material_id: int
    mp_id: str
    pretty_formula: str
    formula: str
    material_type: str | None
    is_stable: bool
    energy_above_hull: float | None

    similarity_score: float

    criticality_score: float | None
    criticality_delta: float | None
    criticality_direction: str

    shared_element_count: int
    shared_application_count: int
    relationship_types: list[str]

    recommendation_score: float
    recommendation_reason: str

class MaterialRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    mp_id: str | None
    pretty_formula: str | None
    formula: str | None
    criticality_score: float | None

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


class MaterialScenarioRecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    mp_id: str | None
    pretty_formula: str | None
    formula: str | None
    criticality_score: float | None

    scenario: MaterialRecommendationScenario
    recommendations: list[MaterialScenarioRead]