from sqlalchemy.orm import Session

from app.core.performance import timed_block
from app.services.discovery.explanation_service import DiscoveryExplanationService
from app.services.discovery.scoring_service import (
    SOURCE_DIVERSITY_BONUS,
    DiscoveryScoringService,
)
from app.services.material.family_service import MaterialFamilyService
from app.services.material.recommendation_service import MaterialRecommendationService
from app.services.discovery.warning_service import DiscoveryWarningService
from app.models.element import Element
from app.models.material_element import MaterialElement
from app.utils.chemical_formula import extract_elements
from app.services.discovery.substitution_path_service import (
    DiscoverySubstitutionPathService,
)

class DiscoveryCandidateService:
    def __init__(self, db: Session):
        self.db = db
        self.substitution_path_service = DiscoverySubstitutionPathService()
        self.family_service = MaterialFamilyService(db)
        self.recommendation_service = MaterialRecommendationService(db)
        self.scoring_service = DiscoveryScoringService()
        self.explanation_service = DiscoveryExplanationService()
        self.warning_service = DiscoveryWarningService()
        self._elements_map_cache: dict[int, list[str]] | None = None

    def get_discovery_candidates(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        limit: int = 10,
        include_recommendations: bool = True,
        include_scenarios: bool = True,
        include_substitution_paths: bool = True,
    ) -> dict:
        with timed_block(
            f"DiscoveryCandidateService.total material_id={material_id}"
        ):
            with timed_block(
                f"DiscoveryCandidateService.family_lookup material_id={material_id}"
            ):
                family_result = self.family_service.get_material_families(
                    material_id
                )

            if family_result["mp_id"] is None:
                return self._empty_response(
                    material_id,
                    avoid_element,
                    prefer_element,
                )

            with timed_block(
                f"DiscoveryCandidateService.elements_map material_id={material_id}"
            ):
                elements_map = self._get_material_elements_map()

            candidates_by_id: dict[int, dict] = {}

            with timed_block(
                f"DiscoveryCandidateService.family_candidates material_id={material_id}"
            ):
                self._add_family_candidates(
                    candidates_by_id=candidates_by_id,
                    family_result=family_result,
                    avoid_element=avoid_element,
                    prefer_element=prefer_element,
                    elements_map=elements_map,
                    include_substitution_paths=include_substitution_paths,
                )

            if include_recommendations:
                with timed_block(
                    f"DiscoveryCandidateService.recommendations material_id={material_id}"
                ):
                    self._add_recommendation_candidates(
                        candidates_by_id=candidates_by_id,
                        material_id=material_id,
                        avoid_element=avoid_element,
                        prefer_element=prefer_element,
                        limit=limit,
                        elements_map=elements_map,
                    )

            if include_scenarios:
                with timed_block(
                    f"DiscoveryCandidateService.scenarios material_id={material_id}"
                ):
                    self._add_scenario_candidates(
                        candidates_by_id=candidates_by_id,
                        material_id=material_id,
                        avoid_element=avoid_element,
                        prefer_element=prefer_element,
                        limit=limit,
                        elements_map=elements_map,
                    )

            with timed_block(
                f"DiscoveryCandidateService.sort material_id={material_id}"
            ):
                all_candidates = sorted(
                    candidates_by_id.values(),
                    key=lambda item: item["discovery_score"],
                    reverse=True,
                )

                candidates = all_candidates[:limit]

            with timed_block(
                f"DiscoveryCandidateService.warnings material_id={material_id}"
            ):
                discovery_warnings = self.warning_service.build_warnings(
                    candidates=candidates,
                    avoid_element=avoid_element,
                    prefer_element=prefer_element,
                    limit=limit,
                    total_candidate_count=len(all_candidates),
                )

            for candidate in candidates:
                candidate.pop("_explanation_parts", None)
                candidate.pop("_source_types", None)
                candidate.pop("_base_discovery_score", None)
                candidate.pop("_base_score_breakdown", None)

            return {
                "material_id": family_result["material_id"],
                "mp_id": family_result["mp_id"],
                "base_formula": (
                    family_result["pretty_formula"]
                    or family_result["formula"]
                ),
                "discovery_goal": {
                    "avoid_element": avoid_element,
                    "prefer_element": prefer_element,
                },
                "discovery_warnings": discovery_warnings,
                "candidates": candidates,
            }

    def _get_material_elements_map(self) -> dict[int, list[str]]:
        if self._elements_map_cache is not None:
            return self._elements_map_cache

        rows = (
            self.db.query(
                MaterialElement.material_id,
                Element.symbol,
            )
            .join(Element, MaterialElement.element_id == Element.id)
            .all()
        )

        elements_map: dict[int, set[str]] = {}

        for material_id, symbol in rows:
            elements_map.setdefault(material_id, set()).add(symbol)

        self._elements_map_cache = {
            material_id: sorted(symbols)
            for material_id, symbols in elements_map.items()
        }

        return self._elements_map_cache

    def _add_family_candidates(
        self,
        candidates_by_id: dict[int, dict],
        family_result: dict,
        avoid_element: str | None,
        prefer_element: str | None,
        elements_map: dict[int, list[str]],
        include_substitution_paths: bool,
    ) -> None:
        base_formula = family_result["pretty_formula"] or family_result["formula"]
        base_elements = elements_map.get(family_result["material_id"], [])

        for candidate in family_result["related_materials"]:
            candidate_formula = candidate["pretty_formula"] or candidate["formula"]
            candidate_elements = elements_map.get(candidate["material_id"], [])
            substitution_path = None

            if include_substitution_paths:
                substitution_path = self.substitution_path_service.build_path(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    base_elements=base_elements,
                    candidate_elements=candidate_elements,
                    relationships=candidate["relationships"],
                )

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
                substitution_path=substitution_path,
                source_type="family",
                candidate_elements=self._resolve_candidate_elements(
                    material_id=candidate["material_id"],
                    formula=candidate_formula,
                    elements_map=elements_map,
                ),
            )

    def _add_recommendation_candidates(
        self,
        candidates_by_id: dict[int, dict],
        material_id: int,
        limit: int,
        avoid_element: str | None,
        prefer_element: str | None,
        elements_map: dict[int, list[str]],
    ) -> None:
        recommendation_limit = min(limit * 3, 20)
        recommendation_result = self.recommendation_service.get_recommendations(
            material_id=material_id,
            limit=recommendation_limit,
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
                source_type="recommendation",
                candidate_elements=self._resolve_candidate_elements(
                    material_id=candidate["material_id"],
                    formula=candidate["pretty_formula"] or candidate["formula"],
                    elements_map=elements_map,
                ),
            )

    def _add_scenario_candidates(
        self,
        candidates_by_id: dict[int, dict],
        material_id: int,
        limit: int,
        avoid_element: str | None,
        prefer_element: str | None,
        elements_map: dict[int, list[str]],
    ) -> None:
        recommendation_limit = min(limit * 3, 20)
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
            limit=recommendation_limit,
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
                source_type="scenario",
                candidate_elements=self._resolve_candidate_elements(
                    material_id=candidate["material_id"],
                    formula=candidate["pretty_formula"] or candidate["formula"],
                    elements_map=elements_map,
                ),
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
        source_type: str,
        substitution_path: dict | None = None,
        candidate_elements: set[str] | None = None,
    ) -> None:
        formula_for_check = pretty_formula or formula
        normalized_paths = set(paths)

        adjusted_score, score_breakdown, normalized_paths = (
            self.scoring_service.apply_element_constraints(
                score=score,
                score_breakdown=score_breakdown,
                paths=normalized_paths,
                candidate_elements=candidate_elements,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            )
        )

        existing = candidates_by_id.get(material_id)

        if existing:
            existing_sources = set(existing["_source_types"])
            updated_sources = existing_sources | {source_type}
            updated_diversity_bonus = (
                self.scoring_service.calculate_source_diversity_bonus(
                    updated_sources
                )
            )

            existing_base_score = existing["_base_discovery_score"]

            if existing["discovery_score"] >= adjusted_score:
                selected_base_score = existing_base_score
                selected_score_breakdown = dict(
                    existing["_base_score_breakdown"]
                )
            else:
                selected_base_score = adjusted_score
                selected_score_breakdown = {
                    key: round(value, 2)
                    for key, value in score_breakdown.items()
                }

            existing["_base_discovery_score"] = round(
                selected_base_score,
                2,
            )
            existing["_base_score_breakdown"] = dict(
                selected_score_breakdown
            )
            existing["_source_types"] = updated_sources

            existing["discovery_score"] = round(
                selected_base_score + updated_diversity_bonus,
                2,
            )
            existing["score_breakdown"] = (
                self.scoring_service.set_source_diversity_bonus(
                    selected_score_breakdown,
                    updated_diversity_bonus,
                )
            )
            existing["discovery_path"] = sorted(
                set(existing["discovery_path"]) | normalized_paths
            )

            if (
                existing.get("substitution_path") is None
                and substitution_path is not None
            ):
                existing["substitution_path"] = substitution_path

            existing["_explanation_parts"] = list(
                dict.fromkeys(
                    existing["_explanation_parts"]
                    + explanation_parts
                )
            )

            existing["explanation"] = (
                self.explanation_service.build_explanation(
                    formula=formula_for_check,
                    paths=existing["discovery_path"],
                    explanation_parts=existing[
                        "_explanation_parts"
                    ],
                    avoid_element=avoid_element,
                    prefer_element=prefer_element,
                )
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
            "_source_types": {source_type},
            "_base_discovery_score": round(adjusted_score, 2),
            "_base_score_breakdown": {
                key: round(value, 2)
                for key, value in score_breakdown.items()
            },
            "substitution_path": substitution_path,
        }


    def _resolve_candidate_elements(
        self,
        material_id: int,
        formula: str | None,
        elements_map: dict[int, list[str]],
    ) -> set[str] | None:
        if material_id in elements_map:
            return set(elements_map[material_id])

        parsed_elements = extract_elements(formula)
        return parsed_elements or None

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