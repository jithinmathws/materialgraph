ALKALI_ELEMENTS = {"Li", "Na", "K", "Mg"}
TRANSITION_METALS = {"Fe", "Mn", "Co", "Ni", "Ti", "V", "Cr"}


class DiscoverySubstitutionPathService:
    def build_path(
        self,
        base_formula: str,
        candidate_formula: str,
        base_elements: list[str],
        candidate_elements: list[str],
        relationships: list[str],
    ) -> dict | None:
        base_set = set(base_elements)
        candidate_set = set(candidate_elements)

        replaced_elements = sorted(base_set - candidate_set)
        introduced_elements = sorted(candidate_set - base_set)
        preserved_framework = sorted(base_set & candidate_set)

        if "alkali_substitution" in relationships:
            return {
                "path_type": "alkali_substitution",
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "replaced_elements": [
                    element
                    for element in replaced_elements
                    if element in ALKALI_ELEMENTS
                ],
                "introduced_elements": [
                    element
                    for element in introduced_elements
                    if element in ALKALI_ELEMENTS
                ],
                "preserved_framework": preserved_framework,
                "reason": self._build_alkali_reason(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    replaced_elements=replaced_elements,
                    introduced_elements=introduced_elements,
                    preserved_framework=preserved_framework,
                ),
            }

        if self._has_transition_metal_substitution(
            base_set=base_set,
            candidate_set=candidate_set,
        ):
            return {
                "path_type": "transition_metal_substitution",
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "replaced_elements": [
                    element
                    for element in replaced_elements
                    if element in TRANSITION_METALS
                ],
                "introduced_elements": [
                    element
                    for element in introduced_elements
                    if element in TRANSITION_METALS
                ],
                "preserved_framework": preserved_framework,
                "reason": self._build_transition_metal_reason(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    replaced_elements=replaced_elements,
                    introduced_elements=introduced_elements,
                    preserved_framework=preserved_framework,
                ),
            }

        if len(preserved_framework) >= 3:
            return {
                "path_type": "framework_preserving",
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "replaced_elements": replaced_elements,
                "introduced_elements": introduced_elements,
                "preserved_framework": preserved_framework,
                "reason": (
                    f"{candidate_formula} preserves the main chemistry of "
                    f"{base_formula} through shared "
                    f"{', '.join(preserved_framework)} elements."
                ),
            }

        return None

    def _has_transition_metal_substitution(
        self,
        base_set: set[str],
        candidate_set: set[str],
    ) -> bool:
        base_transition_metals = base_set & TRANSITION_METALS
        candidate_transition_metals = candidate_set & TRANSITION_METALS

        return bool(base_transition_metals or candidate_transition_metals) and (
            base_transition_metals != candidate_transition_metals
        )

    def _build_alkali_reason(
        self,
        base_formula: str,
        candidate_formula: str,
        replaced_elements: list[str],
        introduced_elements: list[str],
        preserved_framework: list[str],
    ) -> str:
        replaced_alkali = [
            element for element in replaced_elements if element in ALKALI_ELEMENTS
        ]
        introduced_alkali = [
            element for element in introduced_elements if element in ALKALI_ELEMENTS
        ]

        if replaced_alkali and introduced_alkali:
            return (
                f"{candidate_formula} is reachable from {base_formula} by replacing "
                f"{', '.join(replaced_alkali)} with {', '.join(introduced_alkali)} "
                f"while preserving {', '.join(preserved_framework)} chemistry."
            )

        if introduced_alkali:
            return (
                f"{candidate_formula} introduces {', '.join(introduced_alkali)} "
                f"while preserving {', '.join(preserved_framework)} chemistry from "
                f"{base_formula}."
            )

        return (
            f"{candidate_formula} follows an alkali-substitution relationship with "
            f"{base_formula} while preserving "
            f"{', '.join(preserved_framework)} chemistry."
        )

    def _build_transition_metal_reason(
        self,
        base_formula: str,
        candidate_formula: str,
        replaced_elements: list[str],
        introduced_elements: list[str],
        preserved_framework: list[str],
    ) -> str:
        replaced_transition_metals = [
            element for element in replaced_elements if element in TRANSITION_METALS
        ]
        introduced_transition_metals = [
            element for element in introduced_elements if element in TRANSITION_METALS
        ]

        return (
            f"{candidate_formula} is related to {base_formula} through "
            f"transition-metal substitution, replacing "
            f"{', '.join(replaced_transition_metals) or 'none'} with "
            f"{', '.join(introduced_transition_metals) or 'none'} while preserving "
            f"{', '.join(preserved_framework)} chemistry."
        )