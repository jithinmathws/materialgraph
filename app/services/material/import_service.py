from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.material.project_service import MaterialCandidate


class MaterialImportService:
    def __init__(self, db: Session):
        self.db = db

    def import_materials(
        self,
        candidates: list[MaterialCandidate],
    ) -> int:
        imported_count = 0

        for candidate in candidates:
            if self._material_exists(candidate.mp_id):
                continue

            material = self._create_material(candidate)

            self.db.flush()

            self._link_elements(
                material_id=material.id,
                elements=candidate.elements,
            )

            imported_count += 1

        self.db.commit()

        return imported_count

    def _material_exists(self, mp_id: str) -> bool:
        return (
            self.db.query(Material)
            .filter(Material.mp_id == mp_id)
            .first()
            is not None
        )

    def _create_material(
        self,
        candidate: MaterialCandidate,
    ) -> Material:
        material = Material(
            mp_id=candidate.mp_id,
            formula=candidate.formula,
            pretty_formula=candidate.pretty_formula,
            band_gap=candidate.band_gap,
            energy_above_hull=candidate.energy_above_hull,
            formation_energy_per_atom=candidate.formation_energy_per_atom,
            density=candidate.density,
            is_stable=candidate.is_stable,
            raw_data=candidate.raw_data,
            source="materials_project",
        )

        self.db.add(material)

        return material

    def _link_elements(
        self,
        material_id: int,
        elements: list[str],
    ) -> None:
        for symbol in elements:
            element = self._get_or_create_element(symbol)

            self.db.add(
                MaterialElement(
                    material_id=material_id,
                    element_id=element.id,
                    fraction=1.0,
                )
            )

    def _get_or_create_element(
        self,
        symbol: str,
    ) -> Element:
        existing = (
            self.db.query(Element)
            .filter(Element.symbol == symbol)
            .first()
        )

        if existing:
            return existing

        element = Element(
            symbol=symbol,
            name=symbol,
        )

        self.db.add(element)
        self.db.flush()

        return element