FAMILY_BONUS = 40.0
SUBSTITUTION_BONUS = 35.0
LOWER_CRITICALITY_BONUS = 30.0
STABILITY_BONUS = 20.0
PREFERRED_ELEMENT_BONUS = 25.0
AVOIDED_ELEMENT_REMOVED_BONUS = 25.0
AVOIDED_ELEMENT_PRESENT_PENALTY = 50.0
SAME_APPLICATION_BONUS = 15.0
SOURCE_DIVERSITY_BONUS = 10.0


NON_ADDITIVE_SCORE_KEYS = {
    "preferred_element_bonus",
    "avoided_element_removed_bonus",
    "avoided_element_present_penalty",
}


class DiscoveryScoringService:
    def score_family_candidate(
        self,
        relationships: list[str],
    ) -> tuple[float, dict[str, float]]:
        score = 0.0
        score_breakdown: dict[str, float] = {}

        if "shared_chemistry" in relationships:
            score += FAMILY_BONUS
            score_breakdown["family_bonus"] = FAMILY_BONUS

        if "alkali_substitution" in relationships:
            score += SUBSTITUTION_BONUS
            score_breakdown["substitution_bonus"] = SUBSTITUTION_BONUS

        return score, score_breakdown

    def score_recommendation_candidate(
        self,
        candidate: dict,
    ) -> tuple[float, list[str], dict[str, float]]:
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

        return score, paths, score_breakdown

    def score_scenario_candidate(
        self,
        candidate: dict,
    ) -> tuple[float, list[str], dict[str, float]]:
        return (
            candidate["scenario_score"],
            ["scenario_recommendation", "scenario_aligned"],
            {"scenario_score": candidate["scenario_score"]},
        )

    def apply_element_constraints(
        self,
        score: float,
        score_breakdown: dict[str, float],
        paths: set[str],
        formula: str,
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> tuple[float, dict[str, float], set[str]]:
        score_breakdown = dict(score_breakdown)

        if prefer_element and prefer_element in formula:
            score += PREFERRED_ELEMENT_BONUS
            paths.add("preferred_element")
            score_breakdown["preferred_element_bonus"] = PREFERRED_ELEMENT_BONUS

        if avoid_element and avoid_element not in formula:
            score += AVOIDED_ELEMENT_REMOVED_BONUS
            paths.add("avoided_element_removed")
            score_breakdown["avoided_element_removed_bonus"] = (
                AVOIDED_ELEMENT_REMOVED_BONUS
            )

        if avoid_element and avoid_element in formula:
            score -= AVOIDED_ELEMENT_PRESENT_PENALTY
            paths.add("contains_avoided_element")
            score_breakdown["avoided_element_present_penalty"] = (
                -AVOIDED_ELEMENT_PRESENT_PENALTY
            )

        return score, score_breakdown, paths

    def merge_score_breakdowns(
        self,
        existing: dict[str, float],
        incoming: dict[str, float],
    ) -> dict[str, float]:
        merged = dict(existing)

        for key, value in incoming.items():
            if key in NON_ADDITIVE_SCORE_KEYS:
                merged[key] = self._merge_non_additive_score(
                    key=key,
                    existing_value=merged.get(key),
                    incoming_value=value,
                )
            else:
                merged[key] = merged.get(key, 0.0) + value

        return {
            key: round(value, 2)
            for key, value in merged.items()
        }

    def apply_source_diversity_bonus(
        self,
        score_breakdown: dict[str, float],
    ) -> dict[str, float]:
        score_breakdown["source_diversity_bonus"] = round(
            score_breakdown.get("source_diversity_bonus", 0.0)
            + SOURCE_DIVERSITY_BONUS,
            2,
        )

        return score_breakdown

    def _merge_non_additive_score(
        self,
        key: str,
        existing_value: float | None,
        incoming_value: float,
    ) -> float:
        if existing_value is None:
            return incoming_value

        if key == "avoided_element_present_penalty":
            return min(existing_value, incoming_value)

        return max(existing_value, incoming_value)