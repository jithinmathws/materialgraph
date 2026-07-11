from math import isfinite

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

            fractions = self._resolve_element_fractions(
                elements=candidate.elements,
                composition_fractions=candidate.composition_fractions,
            )

            material = self._create_material(candidate)
            self.db.flush()

            self._link_elements(
                material_id=material.id,
                elements=candidate.elements,
                fractions=fractions,
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
        fractions: dict[str, float],
    ) -> None:
        for symbol in elements:
            element = self._get_or_create_element(symbol)

            self.db.add(
                MaterialElement(
                    material_id=material_id,
                    element_id=element.id,
                    fraction=fractions[symbol],
                )
            )

    def _resolve_element_fractions(
        self,
        elements: list[str],
        composition_fractions: dict[str, float],
    ) -> dict[str, float]:
        """
        Return validated composition fractions for an imported candidate.

        Materials Project candidates should provide normalized fractions
        through MaterialCandidate.composition_fractions.

        Legacy or manually constructed candidates may not contain structured
        composition. In that case, preserve the historical importer behavior
        of storing 1.0 for each element rather than inventing stoichiometry.
        """
        unique_elements = list(dict.fromkeys(elements))

        if not unique_elements:
            return {}

        if not composition_fractions:
            return {
                symbol: 1.0
                for symbol in unique_elements
            }

        missing_elements = [
            symbol
            for symbol in unique_elements
            if symbol not in composition_fractions
        ]

        unexpected_elements = [
            symbol
            for symbol in composition_fractions
            if symbol not in unique_elements
        ]

        if missing_elements or unexpected_elements:
            raise ValueError(
                "Material candidate element membership does not match "
                "composition fractions: "
                f"missing={missing_elements}, "
                f"unexpected={unexpected_elements}"
            )

        validated_fractions: dict[str, float] = {}

        for symbol in unique_elements:
            fraction = float(composition_fractions[symbol])

            if not isfinite(fraction) or fraction <= 0:
                raise ValueError(
                    "Material candidate contains an invalid composition "
                    f"fraction for element {symbol}: {fraction!r}"
                )

            validated_fractions[symbol] = fraction

        total_fraction = sum(validated_fractions.values())

        if not isfinite(total_fraction) or total_fraction <= 0:
            raise ValueError(
                "Material candidate composition fractions must have "
                "a positive finite total"
            )

        # Normalize again at the persistence boundary. The project adapter
        # already normalizes Materials Project composition, but this prevents
        # malformed internal callers from storing non-normalized weights.
        return {
            symbol: fraction / total_fraction
            for symbol, fraction in validated_fractions.items()
        }

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