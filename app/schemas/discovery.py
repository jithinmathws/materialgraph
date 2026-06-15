from pydantic import BaseModel, Field


class DiscoveryGoal(BaseModel):
    avoid_element: str | None = None
    prefer_element: str | None = None


class DiscoveryCandidate(BaseModel):
    material_id: int
    mp_id: str | None = None
    pretty_formula: str | None = None
    formula: str
    discovery_score: float
    discovery_path: list[str]
    explanation: str


class DiscoveryCandidatesResponse(BaseModel):
    material_id: int
    mp_id: str | None = None
    base_formula: str | None = None
    discovery_goal: DiscoveryGoal
    candidates: list[DiscoveryCandidate]