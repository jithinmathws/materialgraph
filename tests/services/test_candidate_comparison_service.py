from app.schemas.comparison import (
    CandidateComparisonRequest,
)
from app.schemas.screening import CandidateScreeningResult
from app.services.candidate_comparison_service import (
    CandidateComparisonService,
)


def _candidate(
    *,
    material_id: int,
    formula: str,
    score: float,
    risk_score: float | None = 2.0,
    risk_known: bool = True,
) -> CandidateScreeningResult:
    return CandidateScreeningResult(
        material_id=material_id,
        mp_id=f"test-{material_id}",
        formula=formula,
        pretty_formula=formula,
        score=score,
        material_risk_score=risk_score,
        risk_known=risk_known,
        risk_profile_coverage=(
            1.0 if risk_known else 0.0
        ),
        known_risk_element_count=(
            1 if risk_known else 0
        ),
        total_element_count=1,
        risk_evidence_complete=risk_known,
        unknown_risk_elements=(
            [] if risk_known else [formula]
        ),
        risk_penalty=(
            risk_score * 5
            if risk_known and risk_score is not None
            else 0.0
        ),
        elements=[formula],
        contains_scarce_elements=False,
        contains_avoided_elements=False,
        reasons=[],
    )


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
    assert result.comparison_type == "winner"
    assert result.winner_material_id in {6, 12}
    assert result.winner_formula is not None
    assert result.tied_material_ids == []
    assert result.tied_formulas == []
    assert result.score_difference > 0
    assert result.reasons


def test_compare_candidates_returns_none_for_missing_material(
    db_session,
):
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


def test_compare_candidates_returns_explicit_tie(monkeypatch):
    service = CandidateComparisonService.__new__(
        CandidateComparisonService
    )

    material_a = _candidate(
        material_id=2,
        formula="Material-A",
        score=70.0,
    )
    material_b = _candidate(
        material_id=1,
        formula="Material-B",
        score=70.0,
    )

    class FakeScreeningService:
        def screen_candidates(self, request):
            return [material_a, material_b]

    service.screening_service = FakeScreeningService()

    result = service.compare_candidates(
        CandidateComparisonRequest(
            material_a_id=2,
            material_b_id=1,
        )
    )

    assert result is not None
    assert result.comparison_type == "tie"
    assert result.winner_material_id is None
    assert result.winner_formula is None
    assert result.tied_material_ids == [1, 2]
    assert result.tied_formulas == [
        "Material-B",
        "Material-A",
    ]
    assert result.score_difference == 0.0
    assert any(
        "same deterministic screening score"
        in reason.lower()
        for reason in result.reasons
    )
    assert any(
        "neither candidate"
        in reason.lower()
        for reason in result.reasons
    )


def test_tie_result_is_independent_of_request_order():
    service = CandidateComparisonService.__new__(
        CandidateComparisonService
    )

    material_a = _candidate(
        material_id=10,
        formula="A",
        score=80.0,
    )
    material_b = _candidate(
        material_id=20,
        formula="B",
        score=80.0,
    )

    class FakeScreeningService:
        def screen_candidates(self, request):
            return [material_a, material_b]

    service.screening_service = FakeScreeningService()

    first = service.compare_candidates(
        CandidateComparisonRequest(
            material_a_id=10,
            material_b_id=20,
        )
    )

    second = service.compare_candidates(
        CandidateComparisonRequest(
            material_a_id=20,
            material_b_id=10,
        )
    )

    assert first is not None
    assert second is not None

    assert first.comparison_type == "tie"
    assert second.comparison_type == "tie"

    assert first.tied_material_ids == [10, 20]
    assert second.tied_material_ids == [10, 20]

    assert first.winner_material_id is None
    assert second.winner_material_id is None


def test_comparison_preserves_unknown_risk_as_none():
    service = CandidateComparisonService.__new__(
        CandidateComparisonService
    )

    unknown_candidate = _candidate(
        material_id=1,
        formula="A",
        score=70.0,
        risk_score=None,
        risk_known=False,
    )

    known_candidate = _candidate(
        material_id=2,
        formula="B",
        score=60.0,
        risk_score=2.0,
        risk_known=True,
    )

    class FakeScreeningService:
        def screen_candidates(self, request):
            return [
                unknown_candidate,
                known_candidate,
            ]

    service.screening_service = FakeScreeningService()

    result = service.compare_candidates(
        CandidateComparisonRequest(
            material_a_id=1,
            material_b_id=2,
        )
    )

    assert result is not None
    assert result.material_a_risk_score is None
    assert result.material_b_risk_score == 2.0
    assert result.winner_material_id == 1

    assert not any(
        "lower material risk score" in reason.lower()
        for reason in result.reasons
    )


def test_comparison_does_not_claim_unknown_risk_is_lower():
    service = CandidateComparisonService.__new__(
        CandidateComparisonService
    )

    unknown_candidate = _candidate(
        material_id=1,
        formula="A",
        score=70.0,
        risk_score=None,
        risk_known=False,
    )

    known_candidate = _candidate(
        material_id=2,
        formula="B",
        score=60.0,
        risk_score=2.0,
        risk_known=True,
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