import pytest

from app.services.material.composition_backfill_service import (
    MaterialCompositionBackfillService,
)


def test_extract_composition_amounts_returns_structured_values():
    result = (
        MaterialCompositionBackfillService.extract_composition_amounts(
            {
                "composition": {
                    "Li": 4,
                    "Fe": 4,
                    "P": 4,
                    "O": 16,
                }
            }
        )
    )

    assert result == {
        "Li": 4.0,
        "Fe": 4.0,
        "P": 4.0,
        "O": 16.0,
    }


@pytest.mark.parametrize(
    "raw_data",
    [
        None,
        {},
        {"composition": None},
        {"composition": {}},
        {"composition": "LiFePO4"},
    ],
)
def test_extract_composition_amounts_returns_none_when_unavailable(
    raw_data,
):
    result = (
        MaterialCompositionBackfillService.extract_composition_amounts(
            raw_data
        )
    )

    assert result is None


def test_extract_composition_amounts_rejects_non_numeric_amount():
    with pytest.raises(
        ValueError,
        match="non-numeric amount",
    ):
        MaterialCompositionBackfillService.extract_composition_amounts(
            {
                "composition": {
                    "Li": "unknown",
                }
            }
        )