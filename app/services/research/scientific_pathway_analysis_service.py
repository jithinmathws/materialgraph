import time
from loguru import logger

from collections.abc import Collection
from sqlalchemy.orm import Session

from app.services.material.quality_service import MaterialQualityService
from app.utils.chemical_formula import extract_elements
from app.services.research.objective_service import ResearchObjectiveService
from app.services.research.research_evidence_intelligence_service import (
    ResearchEvidenceIntelligenceService,
)
from app.services.research.comparative_research_intelligence_service import (
    ComparativeResearchIntelligenceService,
)
from app.services.research.endpoint_sensitive_research_ranking_service import (
    EndpointSensitiveResearchRankingService,
)


class ScientificPathwayAnalysisService:
    def __init__(self, db: Session):
        self.objective_service = ResearchObjectiveService(db)
        self.quality_service = MaterialQualityService(db)
        self.evidence_service = ResearchEvidenceIntelligenceService()
        self.comparative_service = ComparativeResearchIntelligenceService()
        self.endpoint_ranking_service = EndpointSensitiveResearchRankingService()
        self._quality_cache: dict[int, dict] = {}

    def analyze(self, material_id: int, objective) -> dict:
        start = time.perf_counter()

        chain_start = time.perf_counter()
        result = self.objective_service.generate_chains_for_objective(
            material_id=material_id,
            objective=objective,
        )
        logger.info(
            "Scientific pathway objective chains took {:.3f}s",
            time.perf_counter() - chain_start,
        )

        self._prefetch_material_quality(result["chains"])

        opportunity_start = time.perf_counter()
        opportunities = []

        previous_score: float | None = None
        current_rank = 0

        for position, chain in enumerate(
            result["chains"],
            start=1,
        ):
            score = round(
                chain.get(
                    "scientific_usefulness_score",
                    0.0,
                ),
                2,
            )

            if previous_score is None or score != previous_score:
                current_rank = position
                previous_score = score

            opportunity = self._build_opportunity(
                position=position,
                rank=current_rank,
                chain=chain,
                objective=objective,
            )

            opportunities.append(
                self.evidence_service.enrich_opportunity(
                    opportunity
                )
            )
        logger.info(
            "Scientific pathway opportunity building took {:.3f}s",
            time.perf_counter() - opportunity_start,
        )

        comparison_start = time.perf_counter()
        comparison = self.comparative_service.compare_opportunities(
            opportunities
        )
        logger.info(
            "Scientific pathway comparison took {:.3f}s",
            time.perf_counter() - comparison_start,
        )

        endpoint_ranking_start = time.perf_counter()
        endpoint_sensitive_ranking = (
            self.endpoint_ranking_service.rank_opportunities(opportunities)
        )
        logger.info(
            "Endpoint-sensitive research ranking took {:.3f}s",
            time.perf_counter() - endpoint_ranking_start,
        )

        logger.info(
            "Scientific pathway analysis total took {:.3f}s",
            time.perf_counter() - start,
        )

        return {
            "material_id": result["material_id"],
            "base_formula": result["base_formula"],
            "objective": objective,
            "pathway_opportunities": opportunities,
            "pathway_comparison": comparison,
            "endpoint_sensitive_ranking": endpoint_sensitive_ranking,
            "researcher_decision_required": True,
            "decision_boundary": (
                "MaterialGraph computes, ranks, explains, and contextualizes "
                "pathway opportunities. Researchers remain responsible for "
                "scientific selection, validation, and experimental decisions."
            ),
        }
    

    @staticmethod
    def _build_objective_satisfaction(
        *,
        avoid_elements: Collection[str] | None,
        prefer_elements: Collection[str] | None,
        removed_elements: Collection[str] | None,
        introduced_elements: Collection[str] | None,
    ) -> dict:
        requested_avoid = frozenset(avoid_elements or ())
        requested_prefer = frozenset(prefer_elements or ())
        removed = frozenset(removed_elements or ())
        introduced = frozenset(introduced_elements or ())

        matched_avoid = requested_avoid.intersection(removed)
        unmatched_avoid = requested_avoid.difference(matched_avoid)

        matched_prefer = requested_prefer.intersection(introduced)
        unmatched_prefer = requested_prefer.difference(matched_prefer)

        avoid_coverage = (
            len(matched_avoid) / len(requested_avoid)
            if requested_avoid
            else 1.0
        )
        prefer_coverage = (
            len(matched_prefer) / len(requested_prefer)
            if requested_prefer
            else 1.0
        )

        requested_count = len(requested_avoid) + len(requested_prefer)
        matched_count = len(matched_avoid) + len(matched_prefer)

        overall_coverage = (
            matched_count / requested_count
            if requested_count
            else 1.0
        )

        if overall_coverage == 1.0:
            status = "complete"
            interpretation = (
                "All requested avoid and prefer element objectives are "
                "represented by path-wide removal and introduction events."
            )
        elif matched_count == 0:
            status = "unmatched"
            interpretation = (
                "None of the requested avoid or prefer element objectives "
                "are represented by path-wide removal or introduction events."
            )
        else:
            status = "partial"
            interpretation = (
                "Some requested avoid or prefer element objectives are "
                "represented by path-wide events; unmatched objectives remain."
            )

        return {
            "requested_avoid_elements": sorted(requested_avoid),
            "matched_avoid_elements": sorted(matched_avoid),
            "unmatched_avoid_elements": sorted(unmatched_avoid),
            "requested_prefer_elements": sorted(requested_prefer),
            "matched_prefer_elements": sorted(matched_prefer),
            "unmatched_prefer_elements": sorted(unmatched_prefer),
            "avoid_coverage": round(avoid_coverage, 4),
            "prefer_coverage": round(prefer_coverage, 4),
            "overall_coverage": round(overall_coverage, 4),
            "status": status,
            "interpretation": interpretation,
        }

    @staticmethod
    def _build_endpoint_objective_satisfaction(
        *,
        avoid_elements: Collection[str] | None,
        prefer_elements: Collection[str] | None,
        endpoint_elements: Collection[str] | None,
    ) -> dict:
        requested_avoid = frozenset(avoid_elements or ())
        requested_prefer = frozenset(prefer_elements or ())
        endpoint = frozenset(endpoint_elements or ())

        # An avoid objective is satisfied when the endpoint does not contain
        # the requested avoided element.
        endpoint_matched_avoid = requested_avoid.difference(endpoint)
        endpoint_unmatched_avoid = requested_avoid.intersection(endpoint)

        # A prefer objective is satisfied when the endpoint contains the
        # requested preferred element.
        endpoint_matched_prefer = requested_prefer.intersection(endpoint)
        endpoint_unmatched_prefer = requested_prefer.difference(endpoint)

        endpoint_avoid_coverage = (
            len(endpoint_matched_avoid) / len(requested_avoid)
            if requested_avoid
            else 1.0
        )
        endpoint_prefer_coverage = (
            len(endpoint_matched_prefer) / len(requested_prefer)
            if requested_prefer
            else 1.0
        )

        requested_count = len(requested_avoid) + len(requested_prefer)
        matched_count = (
            len(endpoint_matched_avoid) + len(endpoint_matched_prefer)
        )
        endpoint_overall_coverage = (
            matched_count / requested_count
            if requested_count
            else 1.0
        )

        if endpoint_overall_coverage == 1.0:
            endpoint_status = "complete"
            endpoint_interpretation = (
                "The final endpoint material satisfies all requested avoid "
                "and prefer element objectives."
            )
        elif matched_count == 0:
            endpoint_status = "unmatched"
            endpoint_interpretation = (
                "The final endpoint material satisfies none of the requested "
                "avoid or prefer element objectives."
            )
        else:
            endpoint_status = "partial"
            endpoint_interpretation = (
                "The final endpoint material satisfies some requested avoid "
                "or prefer element objectives; unmatched endpoint objectives remain."
            )

        return {
            "endpoint_matched_avoid_elements": sorted(endpoint_matched_avoid),
            "endpoint_unmatched_avoid_elements": sorted(endpoint_unmatched_avoid),
            "endpoint_matched_prefer_elements": sorted(endpoint_matched_prefer),
            "endpoint_unmatched_prefer_elements": sorted(endpoint_unmatched_prefer),
            "endpoint_avoid_coverage": round(endpoint_avoid_coverage, 4),
            "endpoint_prefer_coverage": round(endpoint_prefer_coverage, 4),
            "endpoint_overall_coverage": round(endpoint_overall_coverage, 4),
            "endpoint_status": endpoint_status,
            "endpoint_interpretation": endpoint_interpretation,
        }

    @staticmethod
    def _endpoint_elements(materials: list[dict]) -> list[str]:
        if not materials:
            return []

        endpoint = materials[-1]

        structured_elements = endpoint.get("elements")
        if structured_elements:
            return sorted(set(structured_elements))

        formula = endpoint.get("formula") or endpoint.get("pretty_formula")
        if not formula:
            return []

        return sorted(set(extract_elements(formula)))

    def _build_opportunity(
        self,
        position: int,
        rank: int,
        chain: dict,
        objective,
    ) -> dict:
        materials = chain.get("materials", [])
        transitions = chain.get("transitions", [])
        pathway_id = self._build_pathway_id(materials)
        quality = self._material_quality(materials)
        quality_summary = self._quality_summary(materials, quality)

        removed_elements = self._collect_elements(
            transitions,
            "removed_elements",
        )
        introduced_elements = self._collect_elements(
            transitions,
            "introduced_elements",
        )
        endpoint_elements = self._endpoint_elements(materials)

        path_satisfaction = self._build_objective_satisfaction(
            avoid_elements=getattr(objective, "avoid_elements", None),
            prefer_elements=getattr(objective, "prefer_elements", None),
            removed_elements=removed_elements,
            introduced_elements=introduced_elements,
        )
        endpoint_satisfaction = self._build_endpoint_objective_satisfaction(
            avoid_elements=getattr(objective, "avoid_elements", None),
            prefer_elements=getattr(objective, "prefer_elements", None),
            endpoint_elements=endpoint_elements,
        )

        return {
            "pathway_id": pathway_id,
            "position": position,
            "rank": rank,
            "pathway": {
                "hop_count": chain.get("hop_count"),
                "materials": materials,
                "transitions": transitions,
                "chain_reason": chain.get("chain_reason"),
            },
            "scientific_usefulness_score": chain.get("scientific_usefulness_score", 0.0),
            "score_breakdown": chain.get("score_breakdown", {}),
            "scientific_facts": {
                "transition_types": self._transition_types(transitions),
                "shared_elements": self._common_shared_elements(transitions),
                "preserved_framework": self._common_shared_elements(transitions),
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
                "removed_elements": removed_elements,
                "introduced_elements": introduced_elements,
                "material_quality": quality,
            },
            "objective_satisfaction": {
                **path_satisfaction,
                **endpoint_satisfaction,
            },
            "strengths": self._strengths(chain, transitions),
            "trade_offs": self._tradeoffs(chain, transitions, quality),
            "risks": self._risks(transitions, quality),
            "assumptions": self._assumptions(),
            "confidence": self._confidence(
                score=chain.get("scientific_usefulness_score", 0.0),
                chain=chain,
                quality_summary=quality_summary,
            ),
            "recommended_next_investigation": self._next_investigation(
                chain.get("scientific_usefulness_score", 0.0)
            ),
            "researcher_decision_required": True,
            "quality_summary": quality_summary,
        }


    @staticmethod
    def _build_pathway_id(materials: list[dict]) -> str:
        material_ids = [
            material.get("material_id")
            for material in materials
            if material.get("material_id") is not None
        ]

        if not material_ids:
            raise ValueError(
                "Cannot build pathway_id without pathway material IDs."
            )

        return "pathway:" + "-".join(
            str(material_id)
            for material_id in material_ids
        )


    def _material_quality(self, materials: list[dict]) -> list[dict]:
        qualities = []

        for material in materials:
            material_id = material.get("material_id")

            if material_id is not None:
                qualities.append(self._get_material_quality(material_id))

        return qualities

    def _transition_types(self, transitions: list[dict]) -> list[str]:
        return sorted({
            transition.get("transition_type")
            for transition in transitions
            if transition.get("transition_type")
        })

    def _common_shared_elements(
        self,
        transitions: list[dict],
    ) -> list[str]:
        if not transitions:
            return []

        shared_element_sets: list[set[str]] = []

        for transition in transitions:
            if "shared_elements" in transition:
                transition_elements = transition["shared_elements"]
            else:
                transition_elements = transition.get(
                    "preserved_framework",
                    [],
                )

            shared_element_sets.append(set(transition_elements))

        common_elements = set.intersection(*shared_element_sets)

        return sorted(common_elements)

    def _collect_elements(self, transitions: list[dict], key: str) -> list[str]:
        elements = set()

        for transition in transitions:
            elements.update(transition.get(key, []))

        return sorted(elements)

    def _strengths(self, chain: dict, transitions: list[dict]) -> list[str]:
        strengths = []

        breakdown = chain.get("score_breakdown", {})
        removed = self._collect_elements(transitions, "removed_elements")
        introduced = self._collect_elements(transitions, "introduced_elements")
        shared_elements = self._common_shared_elements(transitions)
        transition_types = self._transition_types(transitions)

        if removed:
            strengths.append(
                f"Removes avoided or replaced element(s): {', '.join(removed)}."
            )

        if introduced:
            strengths.append(
                f"Introduces target or alternative element(s): {', '.join(introduced)}."
            )

        if shared_elements:
            strengths.append(
                f"Maintains shared-element continuity: {'-'.join(shared_elements)}. "
                "Structural preservation is not validated."
            )

        if "alkali_substitution" in transition_types:
            strengths.append(
                "Includes alkali substitution logic, which is chemically interpretable for Li/Na-style alternatives."
            )

        if "family_expansion" in transition_types:
            strengths.append(
                "Continues within a related material family instead of jumping to an unrelated chemistry space."
            )

        if breakdown.get("shared_element_continuity", 0.0) >= 15:
            strengths.append("Transition plausibility score is strong.")

        return strengths or ["Available for structured scientific review."]

    def _tradeoffs(
        self,
        chain: dict,
        transitions: list[dict],
        quality: list[dict],
    ) -> list[str]:
        tradeoffs = []

        if len(transitions) > 1:
            tradeoffs.append("Multi-hop pathway may require deeper scientific interpretation.")

        if chain.get("score_breakdown", {}).get("path_efficiency", 0.0) < 10:
            tradeoffs.append("Path efficiency is lower than a direct single-hop transition.")

        if self._average_quality(quality) < 10:
            tradeoffs.append("Material quality signals are mixed.")

        return tradeoffs or ["No major deterministic trade-off was identified."]

    def _risks(self, transitions: list[dict], quality: list[dict]) -> list[str]:
        risks = [
            "Synthesis feasibility is not guaranteed.",
            "Experimental validation is required.",
            "DFT or domain-specific validation is not replaced by this analysis.",
        ]

        if not transitions:
            risks.append("No transition evidence is available.")

        if any(item.get("energy_above_hull") is None for item in quality):
            risks.append("Some material stability data may be missing.")

        return risks

    def _assumptions(self) -> list[str]:
        return [
            "Pathway ranking uses existing deterministic scoring services.",
            "Scientific plausibility is based on encoded graph relationships and transition rules.",
            "Material quality depends on currently stored material properties and risk data.",
        ]

    def _confidence_level(self, score: float) -> str:
        if score >= 85:
            return "high"

        if score >= 65:
            return "medium"

        return "low"

    def _confidence(
        self,
        score: float,
        chain: dict,
        quality_summary: dict,
    ) -> dict:
        reasons: list[str] = []
        breakdown = chain.get("score_breakdown", {})

        if breakdown.get("shared_element_continuity", 0.0) >= 20:
            reasons.append(
                "Shared-element continuity contributes strongly under the current "
                "deterministic model; structural preservation has not been validated."
            )

        if breakdown.get("objective_alignment", 0.0) >= 20:
            reasons.append(
                "The pathway aligns well with the stated research objective."
            )

        if breakdown.get("shared_element_continuity", 0.0) >= 15:
            reasons.append(
                "Transition plausibility is strong under the encoded deterministic rules."
            )

        if quality_summary.get("average_quality_score", 0.0) >= 12:
            reasons.append(
                "Average material quality is strong based on the currently available "
                "material-property evidence."
            )

        return {
            "level": self._confidence_level(score),
            "reasons": reasons
            or [
                "Confidence reflects the deterministic scientific usefulness score "
                "and does not represent experimental validation."
            ],
        }

    def _next_investigation(self, score: float) -> str:
        if score >= 85:
            return "Prioritize literature review, DFT validation, and property comparison."
        if score >= 65:
            return "Review assumptions, stability, risk, and neighboring alternatives."
        return "Treat as exploratory and validate transition logic before deeper work."

    def _average_quality(self, quality: list[dict]) -> float:
        scores = [item.get("quality_score", 0.0) for item in quality]

        if not scores:
            return 0.0

        return round(sum(scores) / len(scores), 2)

    def _quality_summary(self, materials: list[dict], quality: list[dict]) -> dict:
        if not quality:
            return {
                "average_quality_score": 0.0,
                "overall_quality": "unknown",
                "highest_risk_material": None,
                "lowest_quality_material": None,
            }

        material_by_id = {
            material["material_id"]: material
            for material in materials
        }

        average_quality = round(
            sum(item.get("quality_score", 0.0) for item in quality) / len(quality),
            2,
        )

        highest_risk = max(
            quality,
            key=lambda item: item.get("risk_score", 0.0),
        )

        lowest_quality = min(
            quality,
            key=lambda item: item.get("quality_score", 0.0),
        )

        return {
            "average_quality_score": average_quality,
            "overall_quality": self._quality_label(average_quality),
            "highest_risk_material": self._material_label(
                material_by_id,
                highest_risk["material_id"],
            ),
            "lowest_quality_material": self._material_label(
                material_by_id,
                lowest_quality["material_id"],
            ),
        }

    def _quality_label(self, score: float) -> str:
        if score >= 12:
            return "strong"
        if score >= 8:
            return "moderate"
        if score > 0:
            return "weak"
        return "unknown"

    def _material_label(self, material_by_id: dict[int, dict], material_id: int) -> str:
        material = material_by_id.get(material_id)

        if material is None:
            return str(material_id)

        return material.get("formula") or material.get("pretty_formula") or str(material_id)

    def _get_material_quality(self, material_id: int) -> dict:
        if material_id not in self._quality_cache:
            self._quality_cache[material_id] = (
                self.quality_service.get_material_quality(material_id)
            )

        return self._quality_cache[material_id]

    def _prefetch_material_quality(self, chains: list[dict]) -> None:
        material_ids = list(dict.fromkeys(
            material["material_id"]
            for chain in chains
            for material in chain.get("materials", [])
            if material.get("material_id") is not None
        ))

        if not material_ids:
            return

        self._quality_cache.update(
            self.quality_service.get_material_quality_bulk(material_ids)
        )