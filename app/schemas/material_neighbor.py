from pydantic import BaseModel, ConfigDict


class MaterialNeighborRead(BaseModel):
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
    neighbor_score: int


class MaterialNeighborsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    mp_id: str | None
    pretty_formula: str | None
    formula: str | None
    material_type: str | None = None
    is_stable: bool | None = None
    energy_above_hull: float | None = None

    neighbors: list[MaterialNeighborRead]