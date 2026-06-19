from sqlalchemy.orm import Session

from app.services.discovery_explanation_service import DiscoveryExplanationService
from app.services.discovery_scoring_service import (
    SOURCE_DIVERSITY_BONUS,
    DiscoveryScoringService,
)
from app.services.material_family_service import MaterialFamilyService
from app.services.material_recommendation_service import MaterialRecommendationService
from app.services.discovery_warning_service import DiscoveryWarningService


class DiscoveryCandidateService:
    def __init__(self, db: Session):
        self.family_service = MaterialFamilyService(db)
        self.recommendation_service = MaterialRecommendationService(db)
        self.scoring_service = DiscoveryScoringService()
        self.explanation_service = DiscoveryExplanationService()
        self.warning_service = DiscoveryWarningService()

    def get_discovery_candidates(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        limit: int = 10,
    ) -> dict:
        family_result = self.family_service.get_material_families(material_id)

        if family_result["mp_id"] is None:
            return self._empty_response(material_id, avoid_element, prefer_element)

        candidates_by_id: dict[int, dict] = {}

        self._add_family_candidates(
            candidates_by_id=candidates_by_id,
            family_result=family_result,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
        )

        self._add_recommendation_candidates(
            candidates_by_id=candidates_by_id,
            material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
        )

        self._add_scenario_candidates(
            candidates_by_id=candidates_by_id,
            material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
        )
        
        all_candidates = sorted(
            candidates_by_id.values(),
            key=lambda item: item["discovery_score"],
            reverse=True,
        )

        candidates = all_candidates[:limit]

        discovery_warnings = self.warning_service.build_warnings(
            candidates=candidates,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            limit=limit,
            total_candidate_count=len(all_candidates),
        )

        for candidate in candidates:
            candidate.pop("_explanation_parts", None)

        return {
            "material_id": family_result["material_id"],
            "mp_id": family_result["mp_id"],
            "base_formula": family_result["pretty_formula"] or family_result["formula"],
            "discovery_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
            },
            "discovery_warnings": discovery_warnings,
            "candidates": candidates,
        }

    def _add_family_candidates(
        self,
        candidates_by_id: dict[int, dict],
        family_result: dict,
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> None:
        for candidate in family_result["related_materials"]:
            paths = ["family_related", *candidate["relationships"]]

            score, score_breakdown = self.scoring_service.score_family_candidate(
                relationships=candidate["relationships"],
            )

            self._upsert_candidate(
                candidates_by_id=candidates_by_id,
                material_id=candidate["material_id"],
                mp_id=candidate["mp_id"],
                pretty_formula=candidate["pretty_formula"],
                formula=candidate["formula"],
                score=score,
                paths=paths,
                explanation_parts=[candidate["relationship_reason"]],
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                score_breakdown=score_breakdown,
            )

    def _add_recommendation_candidates(
        self,
        candidates_by_id: dict[int, dict],
        material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> None:
        recommendation_result = self.recommendation_service.get_recommendations(
            material_id=material_id,
            limit=50,
            prefer_lower_criticality=True,
        )

        if recommendation_result["mp_id"] is None:
            return

        for candidate in recommendation_result["recommendations"]:
            score, paths, score_breakdown = (
                self.scoring_service.score_recommendation_candidate(candidate)
            )

            self._upsert_candidate(
                candidates_by_id=candidates_by_id,
                material_id=candidate["material_id"],
                mp_id=candidate["mp_id"],
                pretty_formula=candidate["pretty_formula"],
                formula=candidate["formula"],
                score=score,
                paths=paths,
                explanation_parts=[candidate["recommendation_reason"]],
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                score_breakdown=score_breakdown,
            )

    def _add_scenario_candidates(
        self,
        candidates_by_id: dict[int, dict],
        material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> None:
        if not avoid_element and not prefer_element:
            return

        scenario_element = avoid_element or prefer_element

        if scenario_element is None:
            return

        scenario_result = self.recommendation_service.get_scenario_recommendations(
            material_id=material_id,
            element=scenario_element,
            supply_risk_multiplier=1.0,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            limit=50,
        )

        if scenario_result["mp_id"] is None:
            return

        for candidate in scenario_result["recommendations"]:
            score, paths, score_breakdown = (
                self.scoring_service.score_scenario_candidate(candidate)
            )

            self._upsert_candidate(
                candidates_by_id=candidates_by_id,
                material_id=candidate["material_id"],
                mp_id=candidate["mp_id"],
                pretty_formula=candidate["pretty_formula"],
                formula=candidate["formula"],
                score=score,
                paths=paths,
                explanation_parts=[candidate["scenario_reason"]],
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                score_breakdown=score_breakdown,
            )

    def _upsert_candidate(
        self,
        candidates_by_id: dict[int, dict],
        material_id: int,
        mp_id: str | None,
        pretty_formula: str | None,
        formula: str,
        score: float,
        paths: list[str],
        explanation_parts: list[str],
        avoid_element: str | None,
        prefer_element: str | None,
        score_breakdown: dict[str, float],
    ) -> None:
        formula_for_check = pretty_formula or formula
        normalized_paths = set(paths)

        adjusted_score, score_breakdown, normalized_paths = (
            self.scoring_service.apply_element_constraints(
                score=score,
                score_breakdown=score_breakdown,
                paths=normalized_paths,
                formula=formula_for_check,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            )
        )

        existing = candidates_by_id.get(material_id)

        if existing:
            existing["discovery_score"] = round(
                max(existing["discovery_score"], adjusted_score)
                + SOURCE_DIVERSITY_BONUS,
                2,
            )
            existing["discovery_path"] = sorted(
                set(existing["discovery_path"]) | normalized_paths
            )
            existing["score_breakdown"] = self.scoring_service.merge_score_breakdowns(
                existing["score_breakdown"],
                score_breakdown,
            )
            existing["score_breakdown"] = (
                self.scoring_service.apply_source_diversity_bonus(
                    existing["score_breakdown"]
                )
            )
            existing["_explanation_parts"] = list(
                dict.fromkeys(existing["_explanation_parts"] + explanation_parts)
            )
            existing["explanation"] = self.explanation_service.build_explanation(
                formula=formula_for_check,
                paths=existing["discovery_path"],
                explanation_parts=existing["_explanation_parts"],
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            )
            return

        explanation = self.explanation_service.build_explanation(
            formula=formula_for_check,
            paths=sorted(normalized_paths),
            explanation_parts=explanation_parts,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
        )

        candidates_by_id[material_id] = {
            "material_id": material_id,
            "mp_id": mp_id,
            "pretty_formula": pretty_formula,
            "formula": formula,
            "discovery_score": round(adjusted_score, 2),
            "score_breakdown": {
                key: round(value, 2)
                for key, value in score_breakdown.items()
            },
            "discovery_path": sorted(normalized_paths),
            "explanation": explanation,
            "_explanation_parts": explanation_parts,
        }

    def _empty_response(
        self,
        material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "base_formula": None,
            "discovery_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
            },
            "discovery_warnings": [
                "Material was not found, so discovery candidates could not be generated."
            ],
            "candidates": [],
        }