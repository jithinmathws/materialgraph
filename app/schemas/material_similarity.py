# app/schemas/material_similarity.py

from pydantic import BaseModel, ConfigDict


class SimilarMaterialRead(BaseModel):
    material_id: int
    mp_id: str
    pretty_formula: str
    formula: str
    material_type: str | None
    is_stable: bool
    energy_above_hull: float | None

    shared_element_count: int
    shared_application_count: int
    relationship_types: list[str]

    similarity_score: float
    reason_summary: str

    criticality_score: float | None
    criticality_delta: float | None
    criticality_direction: str


class MaterialSimilarityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    mp_id: str | None
    pretty_formula: str | None
    formula: str | None
    material_type: str | None = None
    is_stable: bool | None = None
    energy_above_hull: float | None = None
    criticality_score: float | None = None

    similar_materials: list[SimilarMaterialRead]