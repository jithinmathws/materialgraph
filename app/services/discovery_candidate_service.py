from sqlalchemy.orm import Session

from app.services.material_family_service import MaterialFamilyService
from app.services.material_recommendation_service import MaterialRecommendationService
from app.services.discovery_substitution_path_service import (
    DiscoverySubstitutionPathService,
)
from app.services.discovery_explanation_service import DiscoveryExplanationService
from app.services.discovery_scoring_service import (
    SOURCE_DIVERSITY_BONUS,
    DiscoveryScoringService,
)


FAMILY_BONUS = 40.0
SUBSTITUTION_BONUS = 35.0
LOWER_CRITICALITY_BONUS = 30.0
STABILITY_BONUS = 20.0
PREFERRED_ELEMENT_BONUS = 25.0
AVOIDED_ELEMENT_REMOVED_BONUS = 25.0
AVOIDED_ELEMENT_PRESENT_PENALTY = 50.0
SAME_APPLICATION_BONUS = 15.0
SOURCE_DIVERSITY_BONUS = 10.0


class DiscoveryCandidateService:
    def __init__(self, db: Session):
        self.db = db
        self.family_service = MaterialFamilyService(db)
        self.recommendation_service = MaterialRecommendationService(db)
        self.substitution_path_service = DiscoverySubstitutionPathService()
        self.scoring_service = DiscoveryScoringService()
        self.explanation_service = DiscoveryExplanationService()

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
            candidates_by_id, family_result, avoid_element, prefer_element
        )
        self._add_recommendation_candidates(
            candidates_by_id, material_id, avoid_element, prefer_element
        )
        self._add_scenario_candidates(
            candidates_by_id, material_id, avoid_element, prefer_element
        )

        candidates = sorted(
            candidates_by_id.values(),
            key=lambda item: item["discovery_score"],
            reverse=True,
        )[:limit]

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
            discovery_path = ["family_related", *candidate["relationships"]]
            score = 0.0
            score_breakdown: dict[str, float] = {}

            if "shared_chemistry" in discovery_path:
                score += FAMILY_BONUS
                score_breakdown["family_bonus"] = FAMILY_BONUS

            if "alkali_substitution" in discovery_path:
                score += SUBSTITUTION_BONUS
                score_breakdown["substitution_bonus"] = SUBSTITUTION_BONUS

            self._upsert_candidate(
                candidates_by_id=candidates_by_id,
                material_id=candidate["material_id"],
                mp_id=candidate["mp_id"],
                pretty_formula=candidate["pretty_formula"],
                formula=candidate["formula"],
                score=score,
                paths=discovery_path,
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
            paths = ["recommendation_engine", "similar_material"]
            score = candidate["recommendation_score"]
            score_breakdown = {
                "recommendation_score": candidate["recommendation_score"],
            }

            if candidate["criticality_direction"] == "LOWER_RISK":
                score += LOWER_CRITICALITY_BONUS
                paths.append("lower_criticality")
                score_breakdown["lower_criticality_bonus"] = LOWER_CRITICALITY_BONUS

            if candidate["is_stable"]:
                score += STABILITY_BONUS
                paths.append("stable_material")
                score_breakdown["stability_bonus"] = STABILITY_BONUS

            if candidate["shared_application_count"] > 0:
                score += SAME_APPLICATION_BONUS
                paths.append("same_application")
                score_breakdown["same_application_bonus"] = SAME_APPLICATION_BONUS

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
            paths = ["scenario_recommendation", "scenario_aligned"]
            score_breakdown = {
                "scenario_score": candidate["scenario_score"],
            }

            self._upsert_candidate(
                candidates_by_id=candidates_by_id,
                material_id=candidate["material_id"],
                mp_id=candidate["mp_id"],
                pretty_formula=candidate["pretty_formula"],
                formula=candidate["formula"],
                score=candidate["scenario_score"],
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
        adjusted_score = score
        score_breakdown = dict(score_breakdown)

        if prefer_element and prefer_element in formula_for_check:
            adjusted_score += PREFERRED_ELEMENT_BONUS
            normalized_paths.add("preferred_element")
            score_breakdown["preferred_element_bonus"] = PREFERRED_ELEMENT_BONUS

        if avoid_element and avoid_element not in formula_for_check:
            adjusted_score += AVOIDED_ELEMENT_REMOVED_BONUS
            normalized_paths.add("avoided_element_removed")
            score_breakdown["avoided_element_removed_bonus"] = (
                AVOIDED_ELEMENT_REMOVED_BONUS
            )

        if avoid_element and avoid_element in formula_for_check:
            adjusted_score -= AVOIDED_ELEMENT_PRESENT_PENALTY
            normalized_paths.add("contains_avoided_element")
            score_breakdown["avoided_element_present_penalty"] = (
                -AVOIDED_ELEMENT_PRESENT_PENALTY
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
            existing["score_breakdown"]["source_diversity_bonus"] = round(
                existing["score_breakdown"].get("source_diversity_bonus", 0.0)
                + SOURCE_DIVERSITY_BONUS,
                2,
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
            "candidates": [],
        }