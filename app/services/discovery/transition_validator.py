from app.services.discovery.substitution_path_service import (
    DiscoverySubstitutionPathService,
)


class DiscoveryTransitionValidator:
    VALID_RELATIONSHIPS = {
        "alkali_substitution",
        "shared_chemistry",
        "phosphate_related",
        "transition_metal_related",
        "oxide_related",
    }

    STRONG_RELATIONSHIPS = {
        "alkali_substitution",
        "phosphate_related",
        "shared_chemistry",
    }

    def __init__(self):
        self.substitution_path_service = DiscoverySubstitutionPathService()

    def validate_transition(
        self,
        from_material: dict,
        to_material: dict,
        from_elements: list[str],
        to_elements: list[str],
        relationships: list[str],
        avoid_element: str | None = None,
        prefer_element: str | None = None,
    ) -> dict | None:
        if not self._has_valid_relationship(relationships):
            return None

        if self._violates_avoid_element(
            from_elements=from_elements,
            to_elements=to_elements,
            avoid_element=avoid_element,
        ):
            return None

        substitution_path = self.substitution_path_service.build_path(
            base_formula=from_material["formula"],
            candidate_formula=to_material["formula"],
            base_elements=from_elements,
            candidate_elements=to_elements,
            relationships=relationships,
        )

        shared_elements = sorted(set(from_elements) & set(to_elements))
        preserved_framework = shared_elements  # Backward-compatible alias.
        removed_elements = sorted(set(from_elements) - set(to_elements))
        introduced_elements = sorted(set(to_elements) - set(from_elements))

        transition_type = self._select_transition_type(
            relationships=relationships,
            substitution_path=substitution_path,
        )

        family = self._infer_family(relationships)

        reason = self._build_reason(
            from_formula=from_material["formula"],
            to_formula=to_material["formula"],
            transition_type=transition_type,
            family=family,
            shared_elements=shared_elements,
            removed_elements=removed_elements,
            introduced_elements=introduced_elements,
            prefer_element=prefer_element,
        )

        return {
            "from_material_id": from_material["material_id"],
            "to_material_id": to_material["material_id"],
            "from_formula": from_material["formula"],
            "to_formula": to_material["formula"],
            "transition_type": transition_type,
            "family": family,
            "reason": reason,
            "shared_elements": shared_elements,
            "preserved_framework": preserved_framework,
            "preservation_basis": "element_overlap",
            "structural_preservation_validated": False,
            "removed_elements": removed_elements,
            "introduced_elements": introduced_elements,
        }

    def _has_valid_relationship(self, relationships: list[str]) -> bool:
        relationship_set = set(relationships)

        if not relationship_set & self.VALID_RELATIONSHIPS:
            return False

        return bool(relationship_set & self.STRONG_RELATIONSHIPS)

    def _violates_avoid_element(
        self,
        from_elements: list[str],
        to_elements: list[str],
        avoid_element: str | None,
    ) -> bool:
        if avoid_element is None:
            return False

        from_set = set(from_elements)
        to_set = set(to_elements)

        if avoid_element in from_set and avoid_element not in to_set:
            return False

        if avoid_element not in from_set and avoid_element in to_set:
            return True

        return False

    def _infer_family(
        self,
        relationships: list[str],
    ) -> str | None:
        relationship_set = set(relationships)

        if "phosphate_related" in relationship_set:
            return "phosphate"

        if "oxide_related" in relationship_set:
            return "oxide"

        return None

    def _select_transition_type(
        self,
        relationships: list[str],
        substitution_path: dict | None,
    ) -> str:
        relationship_set = set(relationships)

        if "alkali_substitution" in relationship_set:
            return "alkali_substitution"

        if "phosphate_related" in relationship_set:
            return "family_expansion"

        if "oxide_related" in relationship_set:
            return "family_expansion"

        if "shared_chemistry" in relationship_set:
            return "family_expansion"

        if substitution_path:
            return substitution_path["path_type"]

        return "framework_preserving"

    def _build_reason(
        self,
        from_formula: str,
        to_formula: str,
        transition_type: str,
        family: str | None,
        shared_elements: list[str],
        removed_elements: list[str],
        introduced_elements: list[str],
        prefer_element: str | None,
    ) -> str:
        parts = []

        if removed_elements and introduced_elements:
            parts.append(
                f"{', '.join(removed_elements)} is replaced by "
                f"{', '.join(introduced_elements)}"
            )

        if shared_elements:
            parts.append(
                f"sharing {'-'.join(shared_elements)} elements"
            )
            parts.append("structural preservation is not validated")

        if transition_type == "family_expansion" and family:
            parts.append(f"expanding within the {family} material family")

        if prefer_element and prefer_element in introduced_elements:
            parts.append(f"introducing preferred element {prefer_element}")

        if not parts:
            return (
                f"{from_formula} transitions to {to_formula} "
                f"through {transition_type}."
            )

        return f"{from_formula} → {to_formula}: " + "; ".join(parts) + "."