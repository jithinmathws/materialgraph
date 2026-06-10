from pydantic import BaseModel, ConfigDict

from app.schemas.material_common import MaterialSummary, MaterialRelationshipSummary


class MaterialNeighborRead(MaterialSummary, MaterialRelationshipSummary):
    neighbor_score: int


class MaterialNeighborsResponse(MaterialSummary):
    model_config = ConfigDict(from_attributes=True)

    neighbors: list[MaterialNeighborRead]