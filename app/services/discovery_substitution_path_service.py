ALKALI_ELEMENTS = {"Li", "Na", "K", "Mg"}
TRANSITION_METALS = {"Fe", "Mn", "Co", "Ni", "Ti", "V", "Cr"}


class DiscoverySubstitutionPathService:
    def build_substitution_path(
        self,
        base_formula: str,
        candidate_formula: str,
        base_elements: list[str],
        candidate_elements: list[str],
        relationships: list[str],
    ) -> dict | None:
        base_set = set(base_elements)
        candidate_set = set(candidate_elements)

        removed_elements = sorted(base_set - candidate_set)
        introduced_elements = sorted(candidate_set - base_set)
        preserved_elements = sorted(base_set & candidate_set)

        if "alkali_substitution" in relationships:
            return {
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "path_type": "alkali_substitution",
                "replaced_elements": sorted(
                    element for element in removed_elements
                    if element in ALKALI_ELEMENTS
                ),
                "introduced_elements": sorted(
                    element for element in introduced_elements
                    if element in ALKALI_ELEMENTS
                ),
                "preserved_framework": preserved_elements,
                "reason": self._build_reason(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    path_type="alkali_substitution",
                    replaced_elements=removed_elements,
                    introduced_elements=introduced_elements,
                    preserved_elements=preserved_elements,
                ),
            }

        if base_set & TRANSITION_METALS != candidate_set & TRANSITION_METALS:
            return {
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "path_type": "transition_metal_substitution",
                "replaced_elements": sorted(
                    element for element in removed_elements
                    if element in TRANSITION_METALS
                ),
                "introduced_elements": sorted(
                    element for element in introduced_elements
                    if element in TRANSITION_METALS
                ),
                "preserved_framework": preserved_elements,
                "reason": self._build_reason(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    path_type="transition_metal_substitution",
                    replaced_elements=removed_elements,
                    introduced_elements=introduced_elements,
                    preserved_elements=preserved_elements,
                ),
            }

        if len(preserved_elements) >= 3:
            return {
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "path_type": "framework_preserving",
                "replaced_elements": removed_elements,
                "introduced_elements": introduced_elements,
                "preserved_framework": preserved_elements,
                "reason": self._build_reason(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    path_type="framework_preserving",
                    replaced_elements=removed_elements,
                    introduced_elements=introduced_elements,
                    preserved_elements=preserved_elements,
                ),
            }

        return None

    def _build_reason(
        self,
        base_formula: str,
        candidate_formula: str,
        path_type: str,
        replaced_elements: list[str],
        introduced_elements: list[str],
        preserved_elements: list[str],
    ) -> str:
        if path_type == "alkali_substitution":
            return (
                f"{candidate_formula} is reachable from {base_formula} through "
                f"alkali substitution, replacing {', '.join(replaced_elements) or 'none'} "
                f"with {', '.join(introduced_elements) or 'none'} while preserving "
                f"{', '.join(preserved_elements)} chemistry."
            )

        if path_type == "transition_metal_substitution":
            return (
                f"{candidate_formula} is reachable from {base_formula} through "
                f"transition-metal substitution while preserving "
                f"{', '.join(preserved_elements)} chemistry."
            )

        return (
            f"{candidate_formula} preserves the main chemistry of {base_formula} "
            f"through shared {', '.join(preserved_elements)} elements."
        )