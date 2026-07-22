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
        shared_elements = sorted(base_set & candidate_set)
        preserved_framework = shared_elements  # Backward-compatible alias.

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
                "shared_elements": shared_elements,
                "preserved_framework": preserved_framework,
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
                "reason": self._build_alkali_reason(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    replaced_elements=replaced_elements,
                    introduced_elements=introduced_elements,
                    shared_elements=shared_elements,
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
                "shared_elements": shared_elements,
                "preserved_framework": preserved_framework,
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
                "reason": self._build_transition_metal_reason(
                    base_formula=base_formula,
                    candidate_formula=candidate_formula,
                    replaced_elements=replaced_elements,
                    introduced_elements=introduced_elements,
                    shared_elements=shared_elements,
                ),
            }

        if len(shared_elements) >= 3:
            return {
                "path_type": "shared_element_continuity",
                "from_formula": base_formula,
                "to_formula": candidate_formula,
                "replaced_elements": replaced_elements,
                "introduced_elements": introduced_elements,
                "shared_elements": shared_elements,
                # Backward-compatible field name; values represent shared elements.
                "preserved_framework": preserved_framework,
                "preservation_basis": "element_overlap",
                "structural_preservation_validated": False,
                "reason": (
                    f"{candidate_formula} shares {', '.join(shared_elements)} elements "
                    f"with {base_formula}; structural framework preservation is not "
                    "validated."
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
        shared_elements: list[str],
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
                f"while sharing {', '.join(shared_elements)} elements; structural preservation is not validated."
            )

        if introduced_alkali:
            return (
                f"{candidate_formula} introduces {', '.join(introduced_alkali)} "
                f"while sharing {', '.join(shared_elements)} elements with "
                f"{base_formula}."
            )

        return (
            f"{candidate_formula} follows an alkali-substitution relationship with "
            f"{base_formula} while sharing "
            f"{', '.join(shared_elements)} elements; structural preservation is not validated."
        )

    def _build_transition_metal_reason(
        self,
        base_formula: str,
        candidate_formula: str,
        replaced_elements: list[str],
        introduced_elements: list[str],
        shared_elements: list[str],
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
            f"{', '.join(introduced_transition_metals) or 'none'} while sharing "
            f"{', '.join(shared_elements)} elements; structural preservation is not validated."
        )