from collections.abc import Collection

from sqlalchemy.orm import Session

from app.utils.chemical_formula import extract_elements
from app.services.material.quality_service import MaterialQualityService


class DiscoveryPathRankingService:
    SHARED_ELEMENT_CONTINUITY_WEIGHT = 30.0
    OBJECTIVE_WEIGHT = 25.0
    PLAUSIBILITY_WEIGHT = 20.0
    MATERIAL_QUALITY_WEIGHT = 15.0
    EFFICIENCY_WEIGHT = 10.0

    def __init__(self, db: Session | None = None):
        self.db = db
        self.material_quality_service = (
            MaterialQualityService(db)
            if db is not None
            else None
        )

    def rank_path(
        self,
        materials: list[dict],
        transitions: list[dict],
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        avoid_elements: Collection[str] | None = None,
        prefer_elements: Collection[str] | None = None,
    ) -> dict:
        normalized_avoid_elements = self._normalize_elements(
            element=avoid_element,
            elements=avoid_elements,
        )
        normalized_prefer_elements = self._normalize_elements(
            element=prefer_element,
            elements=prefer_elements,
        )

        continuity_score = self._score_shared_element_continuity(
            transitions
        )
        objective_score = self._score_objective_alignment(
            materials=materials,
            transitions=transitions,
            avoid_elements=normalized_avoid_elements,
            prefer_elements=normalized_prefer_elements,
        )
        plausibility_score = (
            self._score_transition_plausibility(transitions)
        )
        efficiency_score = self._score_path_efficiency(
            transitions
        )
        material_quality_score = self._score_material_quality(
            materials
        )

        total_score = round(
            continuity_score
            + objective_score
            + plausibility_score
            + efficiency_score
            + material_quality_score,
            2,
        )

        return {
            "scientific_usefulness_score": total_score,
            "score_breakdown": {
                "shared_element_continuity": continuity_score,
                "objective_alignment": objective_score,
                "transition_plausibility": plausibility_score,
                "path_efficiency": efficiency_score,
                "material_quality": material_quality_score,
            },
            "usefulness_reason": self._build_usefulness_reason(
                materials=materials,
                transitions=transitions,
                avoid_elements=normalized_avoid_elements,
                prefer_elements=normalized_prefer_elements,
            ),
        }

    def _score_shared_element_continuity(
        self,
        transitions: list[dict],
    ) -> float:
        if not transitions:
            return 0.0

        shared_element_sets = [
            set(
                transition.get("shared_elements")
                or transition.get("preserved_framework", [])
            )
            for transition in transitions
            if (
                transition.get("shared_elements")
                or transition.get("preserved_framework")
            )
        ]

        if not shared_element_sets:
            return 0.0

        common_shared_elements = set.intersection(
            *shared_element_sets
        )

        if {"P", "O"}.issubset(common_shared_elements):
            return self.SHARED_ELEMENT_CONTINUITY_WEIGHT

        if "O" in common_shared_elements:
            return round(
                self.SHARED_ELEMENT_CONTINUITY_WEIGHT * 0.7,
                2,
            )

        if common_shared_elements:
            return round(
                self.SHARED_ELEMENT_CONTINUITY_WEIGHT * 0.5,
                2,
            )

        return 0.0

    def _score_objective_alignment(
        self,
        materials: list[dict],
        transitions: list[dict],
        avoid_elements: frozenset[str],
        prefer_elements: frozenset[str],
    ) -> float:
        if not materials or not transitions:
            return 0.0

        if not avoid_elements and not prefer_elements:
            return round(
                self.OBJECTIVE_WEIGHT * 0.5,
                2,
            )

        endpoint_elements = self._endpoint_elements(materials)

        # An empty set means endpoint composition evidence is unavailable
        # or explicitly empty. It must not earn objective credit.
        if not endpoint_elements:
            return 0.0

        half_weight = self.OBJECTIVE_WEIGHT * 0.5
        score = 0.0

        if avoid_elements:
            satisfied_avoided = (
                avoid_elements - endpoint_elements
            )
            avoidance_ratio = (
                len(satisfied_avoided) / len(avoid_elements)
            )
            score += half_weight * avoidance_ratio

        if prefer_elements:
            satisfied_preferred = (
                prefer_elements & endpoint_elements
            )
            preference_ratio = (
                len(satisfied_preferred) / len(prefer_elements)
            )
            score += half_weight * preference_ratio

        return round(score, 2)

    def _score_transition_plausibility(
        self,
        transitions: list[dict],
    ) -> float:
        if not transitions:
            return 0.0

        transition_scores = []

        for transition in transitions:
            transition_type = transition.get(
                "transition_type"
            )
            family = transition.get("family")

            if transition_type == "alkali_substitution":
                transition_scores.append(1.0)
            elif (
                transition_type == "family_expansion"
                and family
            ):
                transition_scores.append(0.85)
            elif transition_type == "shared_element_continuity":
                transition_scores.append(0.75)
            else:
                transition_scores.append(0.5)

        average = (
            sum(transition_scores)
            / len(transition_scores)
        )

        return round(
            self.PLAUSIBILITY_WEIGHT * average,
            2,
        )

    def _score_path_efficiency(self, transitions: list[dict]) -> float:
        hop_count = len(transitions)

        if hop_count == 0:
            return 0.0

        if hop_count == 1:
            return self.EFFICIENCY_WEIGHT

        if hop_count == 2:
            return round(self.EFFICIENCY_WEIGHT * 0.75, 2)

        return round(self.EFFICIENCY_WEIGHT * 0.5, 2)

    def _build_usefulness_reason(
        self,
        materials: list[dict],
        transitions: list[dict],
        avoid_elements: frozenset[str],
        prefer_elements: frozenset[str],
    ) -> str:
        if not transitions:
            return "No discovery path was available for ranking."

        # preserved_framework is retained as a legacy elemental-overlap
        # fallback; it does not establish structural preservation.
        shared_element_sets = [
            set(
                transition.get("shared_elements")
                or transition.get("preserved_framework", [])
            )
            for transition in transitions
            if (
                transition.get("shared_elements")
                or transition.get("preserved_framework")
            )
        ]

        common_shared_elements = sorted(
            set.intersection(*shared_element_sets)
            if shared_element_sets
            else set()
        )

        removed_elements: set[str] = set()
        introduced_elements: set[str] = set()
        transition_types = []

        for transition in transitions:
            removed_elements.update(
                transition.get("removed_elements", [])
            )
            introduced_elements.update(
                transition.get("introduced_elements", [])
            )
            transition_types.append(
                transition.get("transition_type")
            )

        reasons = []

        # Describe transition events independently from endpoint outcomes.
        path_removed = sorted(avoid_elements & removed_elements)
        path_not_removed = sorted(avoid_elements - removed_elements)
        path_introduced = sorted(
            prefer_elements & introduced_elements
        )
        path_not_introduced = sorted(
            prefer_elements - introduced_elements
        )

        if path_removed:
            reasons.append(
                "removes "
                + ", ".join(path_removed)
                + " during the path"
            )

        if path_not_removed:
            reasons.append(
                "does not show removal events during the path for "
                "requested avoided element(s) "
                + ", ".join(path_not_removed)
            )

        if path_introduced:
            reasons.append(
                "introduces "
                + ", ".join(path_introduced)
                + " during the path"
            )

        if path_not_introduced:
            reasons.append(
                "does not show introduction events during the path for "
                "requested preferred element(s) "
                + ", ".join(path_not_introduced)
            )

        # Determine whether authoritative endpoint-composition evidence exists.
        endpoint_composition_available = False

        if materials:
            endpoint = materials[-1]

            if "elements" in endpoint:
                endpoint_composition_available = True
            elif (
                endpoint.get("formula")
                or endpoint.get("pretty_formula")
            ):
                endpoint_composition_available = True

        if endpoint_composition_available:
            endpoint_elements = self._endpoint_elements(materials)

            excluded_avoided = sorted(
                avoid_elements - endpoint_elements
            )
            retained_avoided = sorted(
                avoid_elements & endpoint_elements
            )
            contained_preferred = sorted(
                prefer_elements & endpoint_elements
            )
            missing_preferred = sorted(
                prefer_elements - endpoint_elements
            )

            if excluded_avoided:
                reasons.append(
                    "endpoint excludes requested avoided element(s) "
                    + ", ".join(excluded_avoided)
                )

            if retained_avoided:
                reasons.append(
                    "endpoint still contains requested avoided element(s) "
                    + ", ".join(retained_avoided)
                )

            if contained_preferred:
                reasons.append(
                    "endpoint contains requested preferred element(s) "
                    + ", ".join(contained_preferred)
                )

            if missing_preferred:
                reasons.append(
                    "endpoint does not contain requested preferred "
                    "element(s) "
                    + ", ".join(missing_preferred)
                )
        elif avoid_elements or prefer_elements:
            reasons.append(
                "endpoint composition is unavailable"
            )

        if common_shared_elements:
            reasons.append(
                f"maintains {'-'.join(common_shared_elements)} "
                "shared-element continuity"
            )

        valid_transition_types = [
            item
            for item in transition_types
            if item
        ]

        if valid_transition_types:
            reasons.append(
                "uses "
                + " -> ".join(valid_transition_types)
                + " transition logic"
            )

        if not reasons:
            return (
                "This path is scientifically useful under the "
                "available deterministic transition evidence."
            )

        return (
            "This path is scientifically useful because it "
            + "; ".join(reasons)
            + "."
        )

    def _score_material_quality(
        self,
        materials: list[dict],
    ) -> float:
        if (
            self.material_quality_service is None
            or not materials
        ):
            return 0.0

        material_ids = [
            material["material_id"]
            for material in materials
            if material.get("material_id") is not None
        ]

        if not material_ids:
            return 0.0

        quality_by_id = (
            self.material_quality_service
            .get_material_quality_bulk(material_ids)
        )

        material_scores = [
            quality.get("quality_score", 0.0)
            for quality in quality_by_id.values()
        ]

        if not material_scores:
            return 0.0

        return round(
            sum(material_scores) / len(material_scores),
            2,
        )


    @staticmethod
    def _endpoint_elements(
        materials: list[dict],
    ) -> set[str]:
        if not materials:
            return set()

        endpoint = materials[-1]

        # Structured endpoint composition is authoritative whenever
        # the field is present, including when explicitly empty.
        if "elements" in endpoint:
            elements = endpoint.get("elements")

            if not elements:
                return set()

            return {
                element
                for element in elements
                if element
            }

        formula = (
            endpoint.get("formula")
            or endpoint.get("pretty_formula")
        )

        return extract_elements(formula)


    def _normalize_elements(
        self,
        *,
        element: str | None,
        elements: Collection[str] | None,
    ) -> frozenset[str]:
        normalized = {
            item
            for item in (elements or [])
            if item
        }

        if element:
            normalized.add(element)

        return frozenset(normalized)
