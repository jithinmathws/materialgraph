from pydantic import BaseModel, ConfigDict


class MaterialNeighborhoodNode(BaseModel):
    material_id: int
    mp_id: str
    pretty_formula: str
    formula: str
    material_type: str | None
    is_stable: bool
    energy_above_hull: float | None
    depth: int
    best_score: int


class MaterialNeighborhoodEdge(BaseModel):
    source_material_id: int
    target_material_id: int
    relationship_types: list[str]
    shared_element_count: int
    shared_application_count: int
    edge_score: int


class MaterialNeighborhoodResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    mp_id: str | None
    pretty_formula: str | None
    formula: str | None
    depth: int
    node_count: int = 0
    edge_count: int = 0
    nodes: list[MaterialNeighborhoodNode]
    edges: list[MaterialNeighborhoodEdge]