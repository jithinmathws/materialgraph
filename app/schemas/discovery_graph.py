from pydantic import BaseModel, Field


class DiscoveryGraphGoal(BaseModel):
    avoid_element: str | None = None
    prefer_element: str | None = None
    max_hops: int
    limit: int | None = None


class DiscoveryGraphNode(BaseModel):
    material_id: int
    mp_id: str | None = None
    pretty_formula: str | None = None
    formula: str
    stability_score: float | None = None
    energy_above_hull: float | None = None
    criticality_score: float | None = None
    risk_score: float | None = None
    quality_score: float | None = None


class DiscoveryGraphEdge(BaseModel):
    source_material_id: int
    target_material_id: int
    transition_type: str
    family: str | None = None
    preserved_framework: list[str] = Field(default_factory=list)
    removed_elements: list[str] = Field(default_factory=list)
    introduced_elements: list[str] = Field(default_factory=list)
    scientific_reason: str


class DiscoveryGraphResponse(BaseModel):
    material_id: int
    mp_id: str | None = None
    base_formula: str | None = None
    graph_goal: DiscoveryGraphGoal
    nodes: list[DiscoveryGraphNode]
    edges: list[DiscoveryGraphEdge]


class DiscoverySubgraphResponse(DiscoveryGraphResponse):
    subgraph_filter: dict


class DiscoveryPathResponse(BaseModel):
    material_id: int
    target_material_id: int
    path_found: bool
    hop_count: int | None = None
    materials: list[DiscoveryGraphNode]
    transitions: list[DiscoveryGraphEdge]
    path_reason: str | None = None
    scientific_usefulness_score: float | None = None
    score_breakdown: dict[str, float] | None = None
    usefulness_reason: str | None = None