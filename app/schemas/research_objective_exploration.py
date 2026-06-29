from pydantic import BaseModel, Field

from app.schemas.discovery import DiscoveryChain, ResearchObjective


class ResearchObjectiveExplorationRequest(BaseModel):
    objective: ResearchObjective
    mode: str = Field(default="balanced", pattern="^(balanced|exploratory|strict)$")
    limit: int = Field(default=5, ge=1, le=20)


class ResearchObjectiveCandidate(BaseModel):
    material_id: int
    formula: str | None = None
    score: float
    reasons: list[str]
    warnings: list[str]


class ResearchObjectiveExplorationResponse(BaseModel):
    material_id: int
    base_formula: str | None = None
    objective: ResearchObjective
    mode: str
    ranked_candidates: list[ResearchObjectiveCandidate]
    chains: list[DiscoveryChain]
    warnings: list[str]
    explanation: str