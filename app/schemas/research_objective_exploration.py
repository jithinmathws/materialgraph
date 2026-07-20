from pydantic import BaseModel, Field
from typing import Any, Literal

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
    shared_elements: list[str] = Field(default_factory=list)
    preserved_framework: list[str]
    preservation_basis: str = "element_overlap"
    structural_preservation_validated: bool = False
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

class ObjectiveSatisfaction(BaseModel):
    requested_avoid_elements: list[str] = Field(default_factory=list)
    matched_avoid_elements: list[str] = Field(default_factory=list)
    unmatched_avoid_elements: list[str] = Field(default_factory=list)

    requested_prefer_elements: list[str] = Field(default_factory=list)
    matched_prefer_elements: list[str] = Field(default_factory=list)
    unmatched_prefer_elements: list[str] = Field(default_factory=list)

    avoid_coverage: float = 0.0
    prefer_coverage: float = 0.0
    overall_coverage: float = 0.0

    status: str
    interpretation: str

    endpoint_matched_avoid_elements: list[str] = Field(default_factory=list)
    endpoint_unmatched_avoid_elements: list[str] = Field(default_factory=list)
    endpoint_matched_prefer_elements: list[str] = Field(default_factory=list)
    endpoint_unmatched_prefer_elements: list[str] = Field(default_factory=list)

    endpoint_avoid_coverage: float = 0.0
    endpoint_prefer_coverage: float = 0.0
    endpoint_overall_coverage: float = 0.0

    endpoint_status: str
    endpoint_interpretation: str

class ScientificPathwayOpportunity(BaseModel):
    evidence_summary: EvidenceSummary | None = None
    pathway_id: str
    position: int
    rank: int
    pathway: ScientificPathway
    scientific_usefulness_score: float
    score_breakdown: dict[str, float]
    scientific_facts: ScientificFacts
    objective_satisfaction: ObjectiveSatisfaction
    quality_summary: QualitySummary
    strengths: list[str]
    trade_offs: list[str]
    risks: list[str]
    assumptions: list[str]
    confidence: ConfidenceExplanation
    recommended_next_investigation: str
    researcher_decision_required: bool


class EndpointMaterialReference(BaseModel):
    material_id: int | None = None
    formula: str | None = None
    pretty_formula: str | None = None
    mp_id: str | None = None


class TopRankedPathway(BaseModel):
    pathway_id: str
    position: int
    rank: int | None = None
    endpoint_material: EndpointMaterialReference | None = None
    scientific_usefulness_score: float
    why_it_ranks_highest: list[str]

class PathwayComparison(BaseModel):
    comparison_count: int = 0

    top_ranking_status: Literal[
        "unique",
        "tie",
        "unavailable",
    ] = "unavailable"

    top_score: float | None = None

    top_ranked_pathway: TopRankedPathway | None = None

    top_ranked_pathways: list[TopRankedPathway] = Field(
        default_factory=list
    )

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
    endpoint_sensitive_ranking: dict[str, Any] | None = None
    pathway_comparison: PathwayComparison | dict
    researcher_decision_required: bool
    decision_boundary: str