from collections.abc import Collection

from sqlalchemy.orm import Session

from app.services.material.quality_service import MaterialQualityService


class DiscoveryPathRankingService:
    FRAMEWORK_WEIGHT = 30.0
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

        framework_score = self._score_framework_preservation(
            transitions
        )
        objective_score = self._score_objective_alignment(
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
            framework_score
            + objective_score
            + plausibility_score
            + efficiency_score
            + material_quality_score,
            2,
        )

        return {
            "scientific_usefulness_score": total_score,
            "score_breakdown": {
                "framework_preservation": framework_score,
                "objective_alignment": objective_score,
                "transition_plausibility": plausibility_score,
                "path_efficiency": efficiency_score,
                "material_quality": material_quality_score,
            },
            "usefulness_reason": self._build_usefulness_reason(
                transitions=transitions,
                avoid_elements=normalized_avoid_elements,
                prefer_elements=normalized_prefer_elements,
            ),
        }

    def _score_framework_preservation(
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
            return self.FRAMEWORK_WEIGHT

        if "O" in common_shared_elements:
            return round(
                self.FRAMEWORK_WEIGHT * 0.7,
                2,
            )

        if common_shared_elements:
            return round(
                self.FRAMEWORK_WEIGHT * 0.5,
                2,
            )

        return 0.0

    def _score_objective_alignment(
        self,
        transitions: list[dict],
        avoid_elements: frozenset[str],
        prefer_elements: frozenset[str],
    ) -> float:
        if not transitions:
            return 0.0

        removed_elements = set()
        introduced_elements = set()

        for transition in transitions:
            removed_elements.update(
                transition.get("removed_elements", [])
            )
            introduced_elements.update(
                transition.get("introduced_elements", [])
            )

        if not avoid_elements and not prefer_elements:
            return round(
                self.OBJECTIVE_WEIGHT * 0.5,
                2,
            )

        half_weight = self.OBJECTIVE_WEIGHT * 0.5
        score = 0.0

        if avoid_elements:
            matched_avoided = (
                avoid_elements & removed_elements
            )
            avoidance_ratio = (
                len(matched_avoided) / len(avoid_elements)
            )
            score += half_weight * avoidance_ratio

        if prefer_elements:
            matched_preferred = (
                prefer_elements & introduced_elements
            )
            preference_ratio = (
                len(matched_preferred)
                / len(prefer_elements)
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

    def _score_path_efficiency(
        self,
        transitions: list[dict],
    ) -> float:
        hop_count = len(transitions)

        if hop_count == 0:
            return 0.0

        if hop_count == 1:
            return self.EFFICIENCY_WEIGHT

        if hop_count == 2:
            return round(
                self.EFFICIENCY_WEIGHT * 0.75,
                2,
            )

        if hop_count == 3:
            return round(
                self.EFFICIENCY_WEIGHT * 0.5,
                2,
            )

        return round(
            self.EFFICIENCY_WEIGHT * 0.25,
            2,
        )

    def _build_usefulness_reason(
        self,
        transitions: list[dict],
        avoid_elements: frozenset[str],
        prefer_elements: frozenset[str],
    ) -> str:
        if not transitions:
            return (
                "No discovery path was available for ranking."
            )

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

        removed_elements = set()
        introduced_elements = set()
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

        matched_avoided = sorted(
            avoid_elements & removed_elements
        )
        unmatched_avoided = sorted(
            avoid_elements - removed_elements
        )
        matched_preferred = sorted(
            prefer_elements & introduced_elements
        )
        unmatched_preferred = sorted(
            prefer_elements - introduced_elements
        )

        reasons = []

        if matched_avoided:
            reasons.append(
                "removes requested avoided element(s) "
                + ", ".join(matched_avoided)
            )

        if unmatched_avoided:
            reasons.append(
                "does not show removal events for requested "
                "avoided element(s) "
                + ", ".join(unmatched_avoided)
            )

        if matched_preferred:
            reasons.append(
                "introduces requested preferred element(s) "
                + ", ".join(matched_preferred)
            )

        if unmatched_preferred:
            reasons.append(
                "does not show introduction events for requested "
                "preferred element(s) "
                + ", ".join(unmatched_preferred)
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
                + " → ".join(valid_transition_types)
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
