import pytest

from app.services.material.similarity_service import MaterialSimilarityService


@pytest.fixture
def service() -> MaterialSimilarityService:
    return MaterialSimilarityService.__new__(MaterialSimilarityService)


@pytest.mark.parametrize(
    (
        "source_criticality_score",
        "neighbor_criticality_score",
        "expected_delta",
    ),
    [
        (32.0, 20.0, -12.0),
        (32.0, 40.0, 8.0),
        (32.0, 32.0, 0.0),
        (32.123, 40.126, 8.0),
        (None, 20.0, None),
        (32.0, None, None),
        (None, None, None),
    ],
)
def test_calculate_criticality_delta(
    service,
    source_criticality_score,
    neighbor_criticality_score,
    expected_delta,
):
    result = service._calculate_criticality_delta(
        source_criticality_score=source_criticality_score,
        neighbor_criticality_score=neighbor_criticality_score,
    )

    assert result == expected_delta


@pytest.mark.parametrize(
    ("criticality_delta", "expected_direction"),
    [
        (-12.0, "LOWER_CRITICALITY"),
        (8.0, "HIGHER_CRITICALITY"),
        (0.0, "SAME_CRITICALITY"),
        (None, "UNKNOWN"),
    ],
)
def test_criticality_direction(
    service,
    criticality_delta,
    expected_direction,
):
    assert service._criticality_direction(criticality_delta) == expected_direction