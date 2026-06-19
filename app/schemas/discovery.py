from pydantic import BaseModel


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