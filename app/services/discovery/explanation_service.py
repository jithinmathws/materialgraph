class DiscoveryExplanationService:
    def build_explanation(
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
            reasons.append(f"It contains the preferred element {prefer_element}.")

        if "avoided_element_removed" in paths and avoid_element:
            reasons.append(f"It does not contain the avoided element {avoid_element}.")

        if "contains_avoided_element" in paths and avoid_element:
            reasons.append(
                f"It still contains the avoided element {avoid_element}, "
                "so it is penalized."
            )

        if "lower_criticality" in paths:
            reasons.append("It has lower estimated criticality than the base material.")

        if "stable_material" in paths:
            reasons.append("It is marked as stable in the material dataset.")

        if "same_application" in paths:
            reasons.append(
                "It shares at least one application context with the base material."
            )

        reasons.append(
            "This is a deterministic discovery suggestion and should be validated "
            "for structure, synthesis feasibility, and application performance."
        )

        return " ".join(reasons)