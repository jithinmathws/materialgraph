from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement


class MaterialFamilyService:
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
                "families": [],
            }

        elements_map = self._get_material_elements_map()
        base_elements = elements_map.get(material_id, [])

        candidates = (
            self.db.query(Material)
            .filter(Material.id != material_id)
            .all()
        )

        families = {
            "same_element_family": [],
            "alkali_substitution_family": [],
            "transition_metal_family": [],
            "phosphate_family": [],
            "oxide_family": [],
        }

        for candidate in candidates:
            candidate_elements = elements_map.get(candidate.id, [])

            family_tags = self._classify_family(
                base_elements=base_elements,
                candidate_elements=candidate_elements,
            )

            shared_elements = sorted(
                set(base_elements) & set(candidate_elements)
            )

            for tag in family_tags:
                families[tag].append(
                    {
                        "material_id": candidate.id,
                        "mp_id": candidate.mp_id,
                        "pretty_formula": candidate.pretty_formula,
                        "formula": candidate.formula,
                        "shared_elements": shared_elements,
                    }
                )

        return {
            "material_id": base_material.id,
            "mp_id": base_material.mp_id,
            "pretty_formula": base_material.pretty_formula,
            "formula": base_material.formula,
            "families": families,
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

    def _classify_family(
        self,
        base_elements: list[str],
        candidate_elements: list[str],
    ) -> list[str]:
        tags = []

        base_set = set(base_elements)
        candidate_set = set(candidate_elements)

        shared_elements = base_set & candidate_set

        if len(shared_elements) >= 2:
            tags.append("same_element_family")

        alkali_elements = {"Li", "Na", "K", "Mg"}
        if base_set & alkali_elements and candidate_set & alkali_elements:
            tags.append("alkali_substitution_family")

        transition_metals = {"Fe", "Mn", "Co", "Ni", "Ti", "V", "Cr"}
        if base_set & transition_metals and candidate_set & transition_metals:
            tags.append("transition_metal_family")

        if "P" in base_set and "P" in candidate_set:
            tags.append("phosphate_family")

        if "O" in base_set and "O" in candidate_set:
            tags.append("oxide_family")

        return tags