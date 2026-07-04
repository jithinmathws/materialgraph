class DiscoveryEdgeIntelligenceService:
    def build_edge_intelligence(
        self,
        transition_type: str | None,
        family: str | None,
        preserved_framework: list[str],
        removed_elements: list[str],
        introduced_elements: list[str],
        scientific_reason: str,
    ) -> dict:
        scientific_plausibility = self._calculate_scientific_plausibility(
            transition_type=transition_type,
            family=family,
            preserved_framework=preserved_framework,
            removed_elements=removed_elements,
            introduced_elements=introduced_elements,
        )

        edge_score = self._calculate_edge_score(
            scientific_plausibility=scientific_plausibility,
            preserved_framework=preserved_framework,
            removed_elements=removed_elements,
            introduced_elements=introduced_elements,
        )

        return {
            "scientific_plausibility": scientific_plausibility,
            "edge_score": edge_score,
            "scientific_reason": scientific_reason,
        }

    def _calculate_scientific_plausibility(
        self,
        transition_type: str | None,
        family: str | None,
        preserved_framework: list[str],
        removed_elements: list[str],
        introduced_elements: list[str],
    ) -> float:
        framework = set(preserved_framework)

        if transition_type == "alkali_substitution":
            return 1.0

        if transition_type == "framework_preserving":
            return 0.85

        if transition_type == "family_expansion":
            if family == "phosphate":
                return 0.75

            if framework:
                return 0.7

            return 0.6

        if removed_elements or introduced_elements:
            return 0.55

        return 0.5

    def _calculate_edge_score(
        self,
        scientific_plausibility: float,
        preserved_framework: list[str],
        removed_elements: list[str],
        introduced_elements: list[str],
    ) -> float:
        score = scientific_plausibility * 100

        framework = set(preserved_framework)

        if {"P", "O"}.issubset(framework):
            score += 10

        if "O" in framework:
            score += 5

        if removed_elements and introduced_elements:
            score += 5

        return round(min(score, 100.0), 2)