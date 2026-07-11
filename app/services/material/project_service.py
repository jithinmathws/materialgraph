from dataclasses import dataclass, field
from math import isfinite
from typing import Any

from mp_api.client import MPRester


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
            composition_fractions=self._normalize_composition(
                doc.composition.get_el_amt_dict()
            ),
        )

    @staticmethod
    def _normalize_composition(
        composition: dict[str, float],
    ) -> dict[str, float]:
        """
        Convert absolute stoichiometric amounts into fractions summing to 1.

        Example:
            {"Li": 1, "Fe": 1, "P": 1, "O": 4}

        becomes approximately:
            {
                "Li": 1 / 7,
                "Fe": 1 / 7,
                "P": 1 / 7,
                "O": 4 / 7,
            }
        """
        normalized_amounts: dict[str, float] = {}

        for raw_symbol, raw_amount in composition.items():
            symbol = str(raw_symbol).strip()
            amount = float(raw_amount)

            if not symbol:
                raise ValueError(
                    "Materials Project composition contains an empty element symbol"
                )

            if not isfinite(amount) or amount <= 0:
                raise ValueError(
                    "Materials Project composition contains an invalid amount "
                    f"for element {symbol}: {raw_amount!r}"
                )

            normalized_amounts[symbol] = amount

        total_amount = sum(normalized_amounts.values())

        if total_amount <= 0:
            raise ValueError(
                "Materials Project composition must have a positive total amount"
            )

        return {
            symbol: amount / total_amount
            for symbol, amount in normalized_amounts.items()
        }