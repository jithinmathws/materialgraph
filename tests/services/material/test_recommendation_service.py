import pytest

from app.services.material.recommendation_service import (
    MaterialRecommendationService,
)


@pytest.fixture
def service() -> MaterialRecommendationService:
    return MaterialRecommendationService.__new__(
        MaterialRecommendationService
    )


def build_candidate(
    criticality_direction: str,
    criticality_delta: float | None,
) -> dict:
    return {
        "similarity_score": 100.0,
        "criticality_direction": criticality_direction,
        "criticality_delta": criticality_delta,
        "shared_element_count": 0,
        "shared_application_count": 0,
        "is_stable": False,
        "energy_above_hull": None,
    }


@pytest.mark.parametrize(
    (
        "criticality_direction",
        "criticality_delta",
        "expected_reason",
    ),
    [
        (
            "LOWER_CRITICALITY",
            -12.0,
            "similarity score 100.0; lower criticality by 12.0; "
            "recommendation score 124.0",
        ),
        (
            "HIGHER_CRITICALITY",
            8.0,
            "similarity score 100.0; higher criticality by 8.0; "
            "recommendation score 84.0",
        ),
        (
            "SAME_CRITICALITY",
            0.0,
            "similarity score 100.0; same criticality; "
            "recommendation score 100.0",
        ),
        (
            "UNKNOWN",
            None,
            "similarity score 100.0; recommendation score 100.0",
        ),
    ],
)
def test_build_recommendation_reason_describes_criticality_comparison(
    service,
    criticality_direction,
    criticality_delta,
    expected_reason,
):
    candidate = build_candidate(
        criticality_direction=criticality_direction,
        criticality_delta=criticality_delta,
    )

    recommendation_score = service._calculate_recommendation_score(
        candidate=candidate,
        prefer_lower_criticality=True,
    )

    reason = service._build_recommendation_reason(
        candidate=candidate,
        recommendation_score=recommendation_score,
    )

    assert reason == expected_reason


@pytest.mark.parametrize(
    (
        "criticality_direction",
        "criticality_delta",
        "expected_score",
    ),
    [
        ("LOWER_CRITICALITY", -12.0, 124.0),
        ("HIGHER_CRITICALITY", 8.0, 84.0),
        ("SAME_CRITICALITY", 0.0, 100.0),
        ("UNKNOWN", None, 100.0),
    ],
)
def test_recommendation_score_uses_delta_not_direction(
    service,
    criticality_direction,
    criticality_delta,
    expected_score,
):
    candidate = build_candidate(
        criticality_direction=criticality_direction,
        criticality_delta=criticality_delta,
    )

    score = service._calculate_recommendation_score(
        candidate=candidate,
        prefer_lower_criticality=True,
    )

    assert score == expected_score