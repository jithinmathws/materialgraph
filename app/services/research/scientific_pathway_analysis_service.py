import time
from loguru import logger
from sqlalchemy.orm import Session

from app.services.material.quality_service import MaterialQualityService
from app.services.research.objective_service import ResearchObjectiveService
from app.services.research.research_evidence_intelligence_service import (
    ResearchEvidenceIntelligenceService,
)
from app.services.research.comparative_research_intelligence_service import (
    ComparativeResearchIntelligenceService,
)


class ScientificPathwayAnalysisService:
    def __init__(self, db: Session):
        self.objective_service = ResearchObjectiveService(db)
        self.quality_service = MaterialQualityService(db)
        self.evidence_service = ResearchEvidenceIntelligenceService()
        self.comparative_service = ComparativeResearchIntelligenceService()
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
        opportunities = [
            self.evidence_service.enrich_opportunity(
                self._build_opportunity(index + 1, chain)
            )
            for index, chain in enumerate(result["chains"])
        ]
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
            "researcher_decision_required": True,
            "decision_boundary": (
                "MaterialGraph computes, ranks, explains, and contextualizes "
                "pathway opportunities. Researchers remain responsible for "
                "scientific selection, validation, and experimental decisions."
            ),
        }

    def _build_opportunity(self, rank: int, chain: dict) -> dict:
        materials = chain.get("materials", [])
        transitions = chain.get("transitions", [])
        quality = self._material_quality(materials)
        quality_summary = self._quality_summary(materials, quality)

        return {
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
                "preserved_framework": self._common_preserved_framework(transitions),
                "removed_elements": self._collect_elements(transitions, "removed_elements"),
                "introduced_elements": self._collect_elements(transitions, "introduced_elements"),
                "material_quality": quality,
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

    def _common_preserved_framework(self, transitions: list[dict]) -> list[str]:
        preserved_sets = [
            set(transition.get("preserved_framework", []))
            for transition in transitions
            if transition.get("preserved_framework")
        ]

        if not preserved_sets:
            return []

        return sorted(set.intersection(*preserved_sets))

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
        preserved = self._common_preserved_framework(transitions)
        transition_types = self._transition_types(transitions)

        if removed:
            strengths.append(
                f"Removes avoided or replaced element(s): {', '.join(removed)}."
            )

        if introduced:
            strengths.append(
                f"Introduces target or alternative element(s): {', '.join(introduced)}."
            )

        if preserved:
            strengths.append(
                f"Preserves shared framework chemistry: {'-'.join(preserved)}."
            )

        if "alkali_substitution" in transition_types:
            strengths.append(
                "Includes alkali substitution logic, which is chemically interpretable for Li/Na-style alternatives."
            )

        if "family_expansion" in transition_types:
            strengths.append(
                "Continues within a related material family instead of jumping to an unrelated chemistry space."
            )

        if breakdown.get("transition_plausibility", 0.0) >= 15:
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

    def _confidence(self, score: float, chain: dict, quality_summary: dict) -> dict:
        reasons = []
        breakdown = chain.get("score_breakdown", {})

        if breakdown.get("framework_preservation", 0.0) >= 20:
            reasons.append("Framework preservation score is strong.")

        if breakdown.get("objective_alignment", 0.0) >= 20:
            reasons.append("Pathway aligns well with the stated objective.")

        if breakdown.get("transition_plausibility", 0.0) >= 15:
            reasons.append("Transition plausibility is high.")

        if quality_summary.get("average_quality_score", 0.0) >= 12:
            reasons.append("Average material quality is strong.")

        return {
            "level": self._confidence_level(score),
            "reasons": reasons or ["Confidence is based on the total scientific usefulness score."],
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