from types import SimpleNamespace

from app.services.research.objective_exploration_service import (
    ResearchObjectiveExplorationService,
)


def _objective(*, avoid_elements=None, prefer_elements=None):
    return SimpleNamespace(
        avoid_elements=avoid_elements or [],
        prefer_elements=prefer_elements or [],
        preserve_elements=[],
        target_family=None,
    )


def test_objective_score_does_not_match_n_to_na():
    service = ResearchObjectiveExplorationService.__new__(
        ResearchObjectiveExplorationService
    )
    material = {"formula": "NaFePO4"}

    score = service._score_material(
        material=material,
        transitions=[],
        objective=_objective(prefer_elements=["N"]),
        mode="balanced",
    )

    assert score == 50.0


def test_objective_reasons_only_report_exact_preferred_element():
    service = ResearchObjectiveExplorationService.__new__(
        ResearchObjectiveExplorationService
    )
    material = {"formula": "NaFePO4"}

    reasons = service._build_reasons(
        material=material,
        transitions=[],
        objective=_objective(prefer_elements=["N"]),
    )

    assert "Candidate contains preferred element N." not in reasons


def test_objective_warnings_only_report_exact_avoided_element():
    service = ResearchObjectiveExplorationService.__new__(
        ResearchObjectiveExplorationService
    )
    material = {"formula": "SiO2"}

    warnings = service._build_candidate_warnings(
        material=material,
        objective=_objective(avoid_elements=["S"]),
        mode="strict",
    )

    assert warnings == []
