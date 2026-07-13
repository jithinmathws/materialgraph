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

def test_comparison_does_not_claim_unknown_risk_is_lower(monkeypatch):
    from app.schemas.screening import CandidateScreeningResult

    service = CandidateComparisonService.__new__(
        CandidateComparisonService
    )

    unknown_candidate = CandidateScreeningResult(
        material_id=1,
        mp_id="test-1",
        formula="A",
        pretty_formula="A",
        score=70.0,
        material_risk_score=None,
        risk_known=False,
        risk_profile_coverage=0.0,
        known_risk_element_count=0,
        total_element_count=1,
        risk_evidence_complete=False,
        unknown_risk_elements=["A"],
        risk_penalty=0.0,
        elements=["A"],
        contains_scarce_elements=False,
        contains_avoided_elements=False,
        reasons=["Material risk evidence unavailable."],
    )

    known_candidate = CandidateScreeningResult(
        material_id=2,
        mp_id="test-2",
        formula="B",
        pretty_formula="B",
        score=60.0,
        material_risk_score=2.0,
        risk_known=True,
        risk_profile_coverage=1.0,
        known_risk_element_count=1,
        total_element_count=1,
        risk_evidence_complete=True,
        unknown_risk_elements=[],
        risk_penalty=10.0,
        elements=["B"],
        contains_scarce_elements=False,
        contains_avoided_elements=False,
        reasons=["Material risk score 2.0 applied."],
    )

    reasons = service._build_reasons(
        winner=unknown_candidate,
        loser=known_candidate,
        scarce_elements=[],
        avoid_elements=[],
    )

    assert not any(
        "lower material risk score" in reason.lower()
        for reason in reasons
    )