from sqlalchemy.orm import Session

from app.services.material_family_service import MaterialFamilyService
from app.services.material_recommendation_service import MaterialRecommendationService


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

    def get_discovery_candidates(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        limit: int = 10,
    ) -> dict:
        family_result = self.family_service.get_material_families(material_id)

        if family_result["mp_id"] is None:
            return self._empty_response(
                material_id=material_id,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            )

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

            if "shared_chemistry" in discovery_path:
                score += FAMILY_BONUS

            if "alkali_substitution" in discovery_path:
                score += SUBSTITUTION_BONUS

            self._upsert_candidate(
                candidates_by_id=candidates_by_id,
                material_id=candidate["material_id"],
                mp_id=candidate["mp_id"],
                pretty_formula=candidate["pretty_formula"],
                formula=candidate["formula"],
                score=score,
                paths=discovery_path,
                explanation_parts=[
                    candidate["relationship_reason"],
                ],
                avoid_element=avoid_element,
                prefer_element=prefer_element,
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

            if candidate["criticality_direction"] == "LOWER_RISK":
                score += LOWER_CRITICALITY_BONUS
                paths.append("lower_criticality")

            if candidate["is_stable"]:
                score += STABILITY_BONUS
                paths.append("stable_material")

            if candidate["shared_application_count"] > 0:
                score += SAME_APPLICATION_BONUS
                paths.append("same_application")

            self._upsert_candidate(
                candidates_by_id=candidates_by_id,
                material_id=candidate["material_id"],
                mp_id=candidate["mp_id"],
                pretty_formula=candidate["pretty_formula"],
                formula=candidate["formula"],
                score=score,
                paths=paths,
                explanation_parts=[
                    candidate["recommendation_reason"],
                ],
                avoid_element=avoid_element,
                prefer_element=prefer_element,
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

            self._upsert_candidate(
                candidates_by_id=candidates_by_id,
                material_id=candidate["material_id"],
                mp_id=candidate["mp_id"],
                pretty_formula=candidate["pretty_formula"],
                formula=candidate["formula"],
                score=candidate["scenario_score"],
                paths=paths,
                explanation_parts=[
                    candidate["scenario_reason"],
                ],
                avoid_element=avoid_element,
                prefer_element=prefer_element,
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
    ) -> None:
        formula_for_check = pretty_formula or formula
        normalized_paths = set(paths)
        adjusted_score = score

        if prefer_element and prefer_element in formula_for_check:
            adjusted_score += PREFERRED_ELEMENT_BONUS
            normalized_paths.add("preferred_element")

        if avoid_element and avoid_element not in formula_for_check:
            adjusted_score += AVOIDED_ELEMENT_REMOVED_BONUS
            normalized_paths.add("avoided_element_removed")

        if avoid_element and avoid_element in formula_for_check:
            adjusted_score -= AVOIDED_ELEMENT_PRESENT_PENALTY
            normalized_paths.add("contains_avoided_element")

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
            existing["_explanation_parts"] = list(
                dict.fromkeys(existing["_explanation_parts"] + explanation_parts)
            )
            existing["explanation"] = self._build_explanation(
                formula=formula_for_check,
                paths=existing["discovery_path"],
                explanation_parts=existing["_explanation_parts"],
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            )
            return

        explanation = self._build_explanation(
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
            "discovery_path": sorted(normalized_paths),
            "explanation": explanation,
            "_explanation_parts": explanation_parts,
        }

    def _build_explanation(
        self,
        formula: str,
        paths: list[str],
        explanation_parts: list[str],
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> str:
        reasons = [f"{formula} is identified as a discovery candidate."]

        reasons.extend(explanation_parts)

        if "preferred_element" in paths and prefer_element:
            reasons.append(
                f"It contains the preferred element {prefer_element}."
            )

        if "avoided_element_removed" in paths and avoid_element:
            reasons.append(
                f"It does not contain the avoided element {avoid_element}."
            )

        if "contains_avoided_element" in paths and avoid_element:
            reasons.append(
                f"It still contains the avoided element {avoid_element}, "
                "so it is penalized."
            )

        if "lower_criticality" in paths:
            reasons.append(
                "It has lower estimated criticality than the base material."
            )

        if "stable_material" in paths:
            reasons.append(
                "It is marked as stable in the material dataset."
            )

        if "same_application" in paths:
            reasons.append(
                "It shares at least one application context with the base material."
            )

        reasons.append(
            "This is a deterministic discovery suggestion and should be validated "
            "for structure, synthesis feasibility, and application performance."
        )

        return " ".join(reasons)

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