from types import SimpleNamespace

import pytest

from app.services.material.project_service import MaterialsProjectService


class FakeComposition:
    reduced_formula = "LiFePO4"

    def get_el_amt_dict(self) -> dict[str, float]:
        return {
            "Li": 1.0,
            "Fe": 1.0,
            "P": 1.0,
            "O": 4.0,
        }


class FakeDocument:
    material_id = "mp-19017"
    formula_pretty = "LiFePO4"
    composition = FakeComposition()
    elements = ["Li", "Fe", "P", "O"]
    band_gap = 1.2
    energy_above_hull = 0.0
    formation_energy_per_atom = -2.5
    density = 3.6
    is_stable = True

    def model_dump(self, mode: str) -> dict:
        assert mode == "json"

        return {
            "material_id": "mp-19017",
            "formula_pretty": "LiFePO4",
            "composition": {
                "Li": 1.0,
                "Fe": 1.0,
                "P": 1.0,
                "O": 4.0,
            },
        }


def make_service() -> MaterialsProjectService:
    # Avoid requiring a real MP API key or network request.
    return MaterialsProjectService(api_key="test-api-key")


def test_normalize_doc_preserves_normalized_composition():
    service = make_service()

    candidate = service._normalize_doc(FakeDocument())

    assert candidate.mp_id == "mp-19017"
    assert candidate.formula == "LiFePO4"

    assert candidate.composition_fractions == pytest.approx(
        {
            "Li": 1 / 7,
            "Fe": 1 / 7,
            "P": 1 / 7,
            "O": 4 / 7,
        }
    )

    assert sum(candidate.composition_fractions.values()) == pytest.approx(1.0)


def test_normalize_composition_rejects_empty_composition():
    service = make_service()

    with pytest.raises(
        ValueError,
        match="positive total amount",
    ):
        service._normalize_composition({})


@pytest.mark.parametrize(
    ("composition", "expected_message"),
    [
        ({"Li": 0.0}, "invalid amount"),
        ({"Li": -1.0}, "invalid amount"),
        ({"Li": float("nan")}, "invalid amount"),
        ({"Li": float("inf")}, "invalid amount"),
    ],
)
def test_normalize_composition_rejects_invalid_amounts(
    composition: dict[str, float],
    expected_message: str,
):
    service = make_service()

    with pytest.raises(ValueError, match=expected_message):
        service._normalize_composition(composition)