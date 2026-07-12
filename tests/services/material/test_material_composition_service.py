import pytest

from app.services.material.composition_service import (
    MaterialCompositionService,
)


def test_normalize_amounts_converts_lifepo4_to_fractions():
    result = MaterialCompositionService.normalize_amounts(
        {
            "Li": 1.0,
            "Fe": 1.0,
            "P": 1.0,
            "O": 4.0,
        }
    )

    assert result == pytest.approx(
        {
            "Li": 1 / 7,
            "Fe": 1 / 7,
            "P": 1 / 7,
            "O": 4 / 7,
        }
    )

    assert sum(result.values()) == pytest.approx(1.0)


def test_normalize_fractions_normalizes_non_unit_values():
    result = MaterialCompositionService.normalize_fractions(
        elements=["Li", "Fe", "P", "O"],
        fractions={
            "Li": 1.0,
            "Fe": 1.0,
            "P": 1.0,
            "O": 4.0,
        },
    )

    assert result == pytest.approx(
        {
            "Li": 1 / 7,
            "Fe": 1 / 7,
            "P": 1 / 7,
            "O": 4 / 7,
        }
    )


def test_resolve_import_fractions_preserves_legacy_unknown_weights():
    result = MaterialCompositionService.resolve_import_fractions(
        elements=["Li", "Fe", "P", "O"],
        composition_fractions={},
    )

    assert result == {
        "Li": 1.0,
        "Fe": 1.0,
        "P": 1.0,
        "O": 1.0,
    }


def test_normalize_fractions_rejects_missing_element():
    with pytest.raises(
        ValueError,
        match="element membership does not match",
    ):
        MaterialCompositionService.normalize_fractions(
            elements=["Li", "Fe", "P", "O"],
            fractions={
                "Li": 0.2,
                "Fe": 0.2,
                "P": 0.6,
            },
        )


def test_normalize_fractions_rejects_unexpected_element():
    with pytest.raises(
        ValueError,
        match="element membership does not match",
    ):
        MaterialCompositionService.normalize_fractions(
            elements=["Li", "Fe", "P", "O"],
            fractions={
                "Li": 0.1,
                "Fe": 0.1,
                "P": 0.1,
                "O": 0.6,
                "Na": 0.1,
            },
        )


@pytest.mark.parametrize(
    "invalid_value",
    [
        0.0,
        -1.0,
        float("nan"),
        float("inf"),
    ],
)
def test_normalize_amounts_rejects_invalid_values(
    invalid_value: float,
):
    with pytest.raises(ValueError, match="invalid composition amount"):
        MaterialCompositionService.normalize_amounts(
            {
                "Li": invalid_value,
            }
        )


def test_normalize_amounts_rejects_empty_composition():
    with pytest.raises(
        ValueError,
        match="at least one element",
    ):
        MaterialCompositionService.normalize_amounts({})


def test_resolve_import_fractions_deduplicates_membership():
    result = MaterialCompositionService.resolve_import_fractions(
        elements=["Li", "Li", "O"],
        composition_fractions={
            "Li": 1.0,
            "O": 1.0,
        },
    )

    assert result == pytest.approx(
        {
            "Li": 0.5,
            "O": 0.5,
        }
    )