from dataclasses import dataclass, field
from typing import Any

from mp_api.client import MPRester
from app.services.material.composition_service import (
    MaterialCompositionService,
)


@dataclass(frozen=True)
class MaterialCandidate:
    mp_id: str
    formula: str
    pretty_formula: str
    elements: list[str]
    band_gap: float | None
    energy_above_hull: float | None
    formation_energy_per_atom: float | None
    density: float | None
    is_stable: bool
    raw_data: dict[str, Any]

    # Normalized stoichiometric composition.
    #
    # Kept optional for compatibility with existing test fixtures and any
    # internal callers that construct MaterialCandidate directly.
    composition_fractions: dict[str, float] = field(default_factory=dict)


class MaterialsProjectService:
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Materials Project API key is required")

        self.api_key = api_key

    def fetch_materials(
        self,
        chemsys: str,
        limit: int = 25,
    ) -> list[MaterialCandidate]:
        fields = [
            "material_id",
            "formula_pretty",
            "composition",
            "elements",
            "band_gap",
            "energy_above_hull",
            "formation_energy_per_atom",
            "density",
            "is_stable",
        ]

        with MPRester(self.api_key) as mpr:
            docs = mpr.materials.summary.search(
                chemsys=chemsys,
                is_stable=True,
                fields=fields,
                num_chunks=1,
                chunk_size=limit,
            )

        return [self._normalize_doc(doc) for doc in docs]

    def _normalize_doc(self, doc: Any) -> MaterialCandidate:
        return MaterialCandidate(
            mp_id=str(doc.material_id),
            formula=str(doc.composition.reduced_formula),
            pretty_formula=str(doc.formula_pretty),
            elements=[str(element) for element in doc.elements],
            band_gap=doc.band_gap,
            energy_above_hull=doc.energy_above_hull,
            formation_energy_per_atom=doc.formation_energy_per_atom,
            density=doc.density,
            is_stable=bool(doc.is_stable),
            raw_data=doc.model_dump(mode="json"),
            composition_fractions=MaterialCompositionService.normalize_amounts(
                doc.composition.get_el_amt_dict()
            ),
        )