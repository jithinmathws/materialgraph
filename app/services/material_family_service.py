from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement


class MaterialFamilyService:
    MIN_SHARED_ELEMENTS = 3

    ALKALI_ELEMENTS = {"Li", "Na", "K", "Mg"}
    TRANSITION_METALS = {"Fe", "Mn", "Co", "Ni", "Ti", "V", "Cr"}
    STRONG_RELATIONSHIPS = {
        "shared_chemistry",
        "alkali_substitution",
        "transition_metal_related",
        "phosphate_related",
    }

    def __init__(self, db: Session):
        self.db = db

    def get_material_families(
        self,
        material_id: int,
    ) -> dict:
        base_material = (
            self.db.query(Material)
            .filter(Material.id == material_id)
            .first()
        )

        if base_material is None:
            return {
                "material_id": material_id,
                "mp_id": None,
                "pretty_formula": None,
                "formula": None,
                "related_materials": [],
            }

        elements_map = self._get_material_elements_map()
        base_elements = elements_map.get(material_id, [])

        candidates = (
            self.db.query(Material)
            .filter(Material.id != material_id)
            .filter(~Material.mp_id.like("mp-test%"))
            .all()
        )

        related_materials = []

        for candidate in candidates:
            candidate_elements = elements_map.get(candidate.id, [])

            relationships = self._classify_relationships(
                base_elements=base_elements,
                candidate_elements=candidate_elements,
            )

            if not self._has_strong_relationship(relationships):
                continue

            shared_elements = sorted(
                set(base_elements) & set(candidate_elements)
            )

            related_materials.append(
                {
                    "material_id": candidate.id,
                    "mp_id": candidate.mp_id,
                    "pretty_formula": candidate.pretty_formula,
                    "formula": candidate.formula,
                    "relationships": relationships,
                    "shared_elements": shared_elements,
                    "relationship_reason": self._build_relationship_reason(
                        base_formula=base_material.formula,
                        candidate_formula=candidate.formula,
                        relationships=relationships,
                        shared_elements=shared_elements,
                        base_elements=base_elements,
                        candidate_elements=candidate_elements,
                    ),
                }
            )

        related_materials.sort(
            key=lambda item: (
                len(item["relationships"]),
                len(item["shared_elements"]),
            ),
            reverse=True,
        )

        return {
            "material_id": base_material.id,
            "mp_id": base_material.mp_id,
            "pretty_formula": base_material.pretty_formula,
            "formula": base_material.formula,
            "related_materials": related_materials,
        }

    def _get_material_elements_map(self) -> dict[int, list[str]]:
        rows = (
            self.db.query(
                MaterialElement.material_id,
                Element.symbol,
            )
            .join(
                Element,
                MaterialElement.element_id == Element.id,
            )
            .all()
        )

        elements_map: dict[int, set[str]] = defaultdict(set)

        for material_id, symbol in rows:
            elements_map[material_id].add(symbol)

        return {
            material_id: sorted(symbols)
            for material_id, symbols in elements_map.items()
        }

    def _classify_relationships(
        self,
        base_elements: list[str],
        candidate_elements: list[str],
    ) -> list[str]:
        relationships = []

        base_set = set(base_elements)
        candidate_set = set(candidate_elements)
        shared_elements = base_set & candidate_set

        if len(shared_elements) >= self.MIN_SHARED_ELEMENTS:
            relationships.append("shared_chemistry")

        if (
            self._has_alkali_substitution(base_set, candidate_set)
            and len(shared_elements) >= self.MIN_SHARED_ELEMENTS
        ):
            relationships.append("alkali_substitution")

        shared_transition_metals = (
            base_set & candidate_set & self.TRANSITION_METALS
        )
        if shared_transition_metals:
            relationships.append("transition_metal_related")

        if "P" in base_set and "P" in candidate_set and "O" in candidate_set:
            relationships.append("phosphate_related")

        if "O" in base_set and "O" in candidate_set:
            relationships.append("oxide_related")

        return relationships

    def _has_strong_relationship(
        self,
        relationships: list[str],
    ) -> bool:
        return bool(set(relationships) & self.STRONG_RELATIONSHIPS)

    def _has_alkali_substitution(
        self,
        base_set: set[str],
        candidate_set: set[str],
    ) -> bool:
        base_alkali = base_set & self.ALKALI_ELEMENTS
        candidate_alkali = candidate_set & self.ALKALI_ELEMENTS

        if not base_alkali or not candidate_alkali:
            return False

        return base_alkali != candidate_alkali

    def _build_relationship_reason(
        self,
        base_formula: str,
        candidate_formula: str,
        relationships: list[str],
        shared_elements: list[str],
        base_elements: list[str],
        candidate_elements: list[str],
    ) -> str:
        reasons = []

        base_set = set(base_elements)
        candidate_set = set(candidate_elements)

        if "shared_chemistry" in relationships:
            reasons.append(
                f"shares {', '.join(shared_elements)} chemistry with {base_formula}"
            )

        if "alkali_substitution" in relationships:
            base_alkali = sorted(base_set & self.ALKALI_ELEMENTS)
            candidate_alkali = sorted(candidate_set & self.ALKALI_ELEMENTS)

            reasons.append(
                "alkali substitution from "
                f"{', '.join(base_alkali)} to {', '.join(candidate_alkali)}"
            )

        if "transition_metal_related" in relationships:
            shared_transition_metals = sorted(
                base_set & candidate_set & self.TRANSITION_METALS
            )
            reasons.append(
                "shares transition metal "
                f"{', '.join(shared_transition_metals)}"
            )

        if "phosphate_related" in relationships:
            reasons.append("shares phosphate framework")

        if "oxide_related" in relationships:
            reasons.append("shares oxide chemistry")

        return (
            f"{candidate_formula}: " + "; ".join(reasons)
            if reasons
            else f"{candidate_formula}: related material candidate"
        )