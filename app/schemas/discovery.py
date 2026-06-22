from pydantic import BaseModel, Field


class DiscoveryGoal(BaseModel):
    avoid_element: str | None = None
    prefer_element: str | None = None


class SubstitutionPath(BaseModel):
    from_formula: str
    to_formula: str
    path_type: str
    replaced_elements: list[str]
    introduced_elements: list[str]
    preserved_framework: list[str]
    reason: str


class DiscoveryCandidate(BaseModel):
    material_id: int
    mp_id: str | None = None
    pretty_formula: str | None = None
    formula: str
    discovery_score: float
    score_breakdown: dict[str, float]
    discovery_path: list[str]
    substitution_path: SubstitutionPath | None = None
    explanation: str


class DiscoveryCandidatesResponse(BaseModel):
    material_id: int
    mp_id: str | None = None
    base_formula: str | None = None
    discovery_goal: DiscoveryGoal
    discovery_warnings: list[str] = []
    candidates: list[DiscoveryCandidate]

class DiscoveryChainGoal(DiscoveryGoal):
    max_hops: int = Field(default=2, ge=1, le=3)
    limit: int = Field(default=5, ge=1, le=20)


class DiscoveryChainMaterial(BaseModel):
    material_id: int
    mp_id: str | None = None
    pretty_formula: str | None = None
    formula: str


class DiscoveryChainTransition(BaseModel):
    from_material_id: int
    to_material_id: int
    from_formula: str
    to_formula: str
    transition_type: str
    family: str | None = None
    reason: str
    preserved_framework: list[str]
    removed_elements: list[str]
    introduced_elements: list[str]


class DiscoveryChain(BaseModel):
    hop_count: int
    materials: list[DiscoveryChainMaterial]
    transitions: list[DiscoveryChainTransition]
    chain_reason: str

    scientific_usefulness_score: float | None = None
    score_breakdown: dict[str, float] | None = None
    usefulness_reason: str | None = None


class DiscoveryChainsResponse(BaseModel):
    material_id: int
    mp_id: str | None = None
    base_formula: str | None = None
    discovery_goal: DiscoveryChainGoal
    chains: list[DiscoveryChain]

class ResearchObjective(BaseModel):
    avoid_elements: list[str] = []
    prefer_elements: list[str] = []
    preserve_elements: list[str] = []
    target_family: str | None = None
    max_hops: int = Field(default=2, ge=1, le=3)
    limit: int = Field(default=5, ge=1, le=20)
    prefer_lower_criticality: bool = True
    require_stable_materials: bool = False


class ResearchObjectiveChainRequest(BaseModel):
    objective: ResearchObjective


class ResearchObjectiveChainResponse(BaseModel):
    material_id: int
    base_formula: str | None = None
    objective: ResearchObjective
    chains: list[DiscoveryChain]