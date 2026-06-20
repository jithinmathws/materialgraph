from app.services.discovery_substitution_path_service import (
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

        preserved_framework = sorted(set(from_elements) & set(to_elements))
        removed_elements = sorted(set(from_elements) - set(to_elements))
        introduced_elements = sorted(set(to_elements) - set(from_elements))

        transition_type = self._select_transition_type(
            relationships=relationships,
            substitution_path=substitution_path,
        )

        reason = self._build_reason(
            from_formula=from_material["formula"],
            to_formula=to_material["formula"],
            transition_type=transition_type,
            preserved_framework=preserved_framework,
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
            "reason": reason,
            "preserved_framework": preserved_framework,
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

    def _select_transition_type(
        self,
        relationships: list[str],
        substitution_path: dict | None,
    ) -> str:
        if substitution_path is not None:
            return substitution_path["path_type"]

        if "alkali_substitution" in relationships:
            return "alkali_substitution"

        if "phosphate_related" in relationships and "shared_chemistry" in relationships:
            return "phosphate_family_expansion"

        if "shared_chemistry" in relationships:
            return "shared_chemistry_transition"

        return relationships[0]

    def _build_reason(
        self,
        from_formula: str,
        to_formula: str,
        transition_type: str,
        preserved_framework: list[str],
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

        if preserved_framework:
            parts.append(
                f"preserving {'-'.join(preserved_framework)} chemistry"
            )

        if transition_type == "phosphate_family_expansion":
            parts.append("within a related phosphate material family")

        if prefer_element and prefer_element in introduced_elements:
            parts.append(f"introducing preferred element {prefer_element}")

        if not parts:
            return f"{from_formula} transitions to {to_formula} through {transition_type}."

        return f"{from_formula} → {to_formula}: " + "; ".join(parts) + "."