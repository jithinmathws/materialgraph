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