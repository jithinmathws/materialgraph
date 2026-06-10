from pydantic import ConfigDict

from app.schemas.material_common import MaterialRiskSummary, MaterialRelationshipSummary


class SimilarMaterialRead(MaterialRiskSummary, MaterialRelationshipSummary):
    similarity_score: float
    reason_summary: str
    criticality_delta: float | None
    criticality_direction: str


class MaterialSimilarityResponse(MaterialRiskSummary):
    model_config = ConfigDict(from_attributes=True)

    similar_materials: list[SimilarMaterialRead]