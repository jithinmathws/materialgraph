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
    ) -> dict:
        framework_score = self._score_framework_preservation(transitions)
        objective_score = self._score_objective_alignment(
            transitions=transitions,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
        )
        plausibility_score = self._score_transition_plausibility(transitions)
        efficiency_score = self._score_path_efficiency(transitions)
        material_quality_score = self._score_material_quality(materials)

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
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            ),
        }

    def _score_framework_preservation(
        self,
        transitions: list[dict],
    ) -> float:
        if not transitions:
            return 0.0

        preserved_sets = [
            set(transition.get("preserved_framework", []))
            for transition in transitions
            if transition.get("preserved_framework")
        ]

        if not preserved_sets:
            return 0.0

        common_framework = set.intersection(*preserved_sets)

        if {"P", "O"}.issubset(common_framework):
            return self.FRAMEWORK_WEIGHT

        if "O" in common_framework:
            return round(self.FRAMEWORK_WEIGHT * 0.7, 2)

        if common_framework:
            return round(self.FRAMEWORK_WEIGHT * 0.5, 2)

        return 0.0

    def _score_objective_alignment(
        self,
        transitions: list[dict],
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> float:
        if not transitions:
            return 0.0

        score = 0.0

        removed_elements = set()
        introduced_elements = set()

        for transition in transitions:
            removed_elements.update(transition.get("removed_elements", []))
            introduced_elements.update(transition.get("introduced_elements", []))

        if avoid_element and avoid_element in removed_elements:
            score += self.OBJECTIVE_WEIGHT * 0.5

        if prefer_element and prefer_element in introduced_elements:
            score += self.OBJECTIVE_WEIGHT * 0.5

        if avoid_element is None and prefer_element is None:
            score = self.OBJECTIVE_WEIGHT * 0.5

        return round(score, 2)

    def _score_transition_plausibility(
        self,
        transitions: list[dict],
    ) -> float:
        if not transitions:
            return 0.0

        transition_scores = []

        for transition in transitions:
            transition_type = transition.get("transition_type")
            family = transition.get("family")

            if transition_type == "alkali_substitution":
                transition_scores.append(1.0)
            elif transition_type == "family_expansion" and family:
                transition_scores.append(0.85)
            elif transition_type == "framework_preserving":
                transition_scores.append(0.75)
            else:
                transition_scores.append(0.5)

        average = sum(transition_scores) / len(transition_scores)

        return round(self.PLAUSIBILITY_WEIGHT * average, 2)

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
            return round(self.EFFICIENCY_WEIGHT * 0.75, 2)

        if hop_count == 3:
            return round(self.EFFICIENCY_WEIGHT * 0.5, 2)

        return round(self.EFFICIENCY_WEIGHT * 0.25, 2)

    def _build_usefulness_reason(
        self,
        transitions: list[dict],
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> str:
        if not transitions:
            return "No discovery path was available for ranking."

        preserved_sets = [
            set(transition.get("preserved_framework", []))
            for transition in transitions
            if transition.get("preserved_framework")
        ]

        common_framework = sorted(
            set.intersection(*preserved_sets)
            if preserved_sets
            else set()
        )

        removed_elements = set()
        introduced_elements = set()
        transition_types = []

        for transition in transitions:
            removed_elements.update(transition.get("removed_elements", []))
            introduced_elements.update(transition.get("introduced_elements", []))
            transition_types.append(transition.get("transition_type"))

        reasons = []

        if avoid_element and avoid_element in removed_elements:
            reasons.append(f"removes avoided element {avoid_element}")

        if prefer_element and prefer_element in introduced_elements:
            reasons.append(f"introduces preferred element {prefer_element}")

        if common_framework:
            reasons.append(
                f"preserves {'-'.join(common_framework)} framework chemistry"
            )

        if transition_types:
            reasons.append(
                "uses "
                + " → ".join(
                    item for item in transition_types if item
                )
                + " transition logic"
            )

        return "This path is scientifically useful because it " + "; ".join(reasons) + "."

    def _score_material_quality(
        self,
        materials: list[dict],
    ) -> float:
        if self.db is None or not materials:
            return 0.0

        material_scores = []

        for material_data in materials:
            material_id = material_data.get("material_id")

            if material_id is None:
                continue

            score = self._score_single_material_quality(material_id)

            material_scores.append(score)

        if not material_scores:
            return 0.0

        return round(
            sum(material_scores) / len(material_scores),
            2,
        )

    def _score_single_material_quality(
        self,
        material_id: int,
    ) -> float:
        if self.material_quality_service is None:
            return 0.0

        return self.material_quality_service.get_material_quality_score(material_id)