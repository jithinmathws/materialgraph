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

class QualitySummary(BaseModel):
    average_quality_score: float
    overall_quality: str
    highest_risk_material: str | None = None
    lowest_quality_material: str | None = None


class ConfidenceExplanation(BaseModel):
    level: str
    reasons: list[str]


class ScientificFacts(BaseModel):
    transition_types: list[str]
    preserved_framework: list[str]
    removed_elements: list[str]
    introduced_elements: list[str]
    material_quality: list[dict]


class ScientificPathway(BaseModel):
    hop_count: int
    materials: list
    transitions: list
    chain_reason: str | None = None


class ScientificPathwayOpportunity(BaseModel):
    evidence_summary: EvidenceSummary | None = None
    rank: int
    pathway: ScientificPathway
    scientific_usefulness_score: float
    score_breakdown: dict[str, float]
    scientific_facts: ScientificFacts
    quality_summary: QualitySummary
    strengths: list[str]
    trade_offs: list[str]
    risks: list[str]
    assumptions: list[str]
    confidence: ConfidenceExplanation
    recommended_next_investigation: str
    researcher_decision_required: bool


class PathwayComparison(BaseModel):
    highest_scoring_pathway_rank: int | None = None
    highest_quality_pathway_rank: int | None = None
    most_direct_pathway_rank: int | None = None
    lowest_risk_pathway_rank: int | None = None


class ScientificPathwayAnalysisResponse(BaseModel):
    material_id: int
    base_formula: str | None = None
    objective: ResearchObjective
    pathway_opportunities: list[ScientificPathwayOpportunity]
    pathway_comparison: PathwayComparison | dict
    researcher_decision_required: bool
    decision_boundary: str

class EvidenceSummary(BaseModel):
    supporting_signals: list[str]
    missing_evidence: list[str]
    weak_assumptions: list[str]
    validation_priorities: list[str]
    evidence_confidence: str