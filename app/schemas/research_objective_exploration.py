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

class SupportingSignal(BaseModel):
    statement: str
    source_service: str
    derived_from: str
    confidence: str


class MissingEvidence(BaseModel):
    statement: str
    reason: str
    researcher_action: str


class WeakAssumption(BaseModel):
    assumption: str
    based_on: str
    requires_validation: bool = True


class ValidationPriority(BaseModel):
    priority: int
    action: str
    reason: str


class EvidenceSummary(BaseModel):
    supporting_signals: list[SupportingSignal]
    missing_evidence: list[MissingEvidence]
    weak_assumptions: list[WeakAssumption]
    validation_priorities: list[ValidationPriority]
    evidence_readiness: str

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
    comparison_count: int = 0
    top_ranked_pathway: dict | None = None
    comparative_strengths: list[dict] = Field(default_factory=list)
    comparative_trade_offs: list[dict] = Field(default_factory=list)
    comparative_research_gaps: list[dict] = Field(default_factory=list)
    comparative_evidence_readiness: dict = Field(default_factory=dict)
    comparative_assumptions: list[dict] = Field(default_factory=list)
    pairwise_comparisons: list[dict] = Field(default_factory=list)
    comparative_element_highlights: list[dict] = Field(default_factory=list)
    researcher_decision_required: bool = True
    decision_boundary: str


class ScientificPathwayAnalysisResponse(BaseModel):
    material_id: int
    base_formula: str | None = None
    objective: ResearchObjective
    pathway_opportunities: list[ScientificPathwayOpportunity]
    pathway_comparison: PathwayComparison | dict
    researcher_decision_required: bool
    decision_boundary: str