from app.schemas.comparison import CandidateComparisonRequest
from app.services.candidate_comparison_service import CandidateComparisonService


def test_compare_candidates_returns_winner(db_session):
    service = CandidateComparisonService(db_session)

    result = service.compare_candidates(
        CandidateComparisonRequest(
            material_a_id=6,
            material_b_id=12,
            scarce_elements=["Li"],
            avoid_elements=["Co"],
            require_stable=True,
            max_energy_above_hull=0.05,
        )
    )

    assert result is not None
    assert result.winner_material_id in {6, 12}
    assert result.score_difference >= 0
    assert len(result.reasons) > 0


def test_compare_candidates_returns_none_for_missing_material(db_session):
    service = CandidateComparisonService(db_session)

    result = service.compare_candidates(
        CandidateComparisonRequest(
            material_a_id=6,
            material_b_id=999999,
            scarce_elements=["Li"],
            avoid_elements=["Co"],
        )
    )

    assert result is None