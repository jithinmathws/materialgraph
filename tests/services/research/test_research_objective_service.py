def test_research_objective_chains_include_ranking_fields(db_session):
    from app.schemas.discovery import ResearchObjective
    from app.services.research.objective_service import ResearchObjectiveService

    service = ResearchObjectiveService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
        prefer_lower_criticality=True,
        require_stable_materials=False,
    )

    result = service.generate_chains_for_objective(
        material_id=5,
        objective=objective,
    )

    assert result["material_id"] == 5
    assert result["chains"]

    for chain in result["chains"]:
        assert "scientific_usefulness_score" in chain
        assert "score_breakdown" in chain
        assert "usefulness_reason" in chain


def test_research_objective_chains_are_sorted_by_usefulness(db_session):
    from app.schemas.discovery import ResearchObjective
    from app.services.research.objective_service import ResearchObjectiveService

    service = ResearchObjectiveService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.generate_chains_for_objective(
        material_id=5,
        objective=objective,
    )

    scores = [
        chain["scientific_usefulness_score"]
        for chain in result["chains"]
    ]

    assert scores == sorted(scores, reverse=True)


def test_research_objective_filters_preserved_elements(db_session):
    from app.schemas.discovery import ResearchObjective
    from app.services.research.objective_service import ResearchObjectiveService

    service = ResearchObjectiveService(db_session)

    objective = ResearchObjective(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
    )

    result = service.generate_chains_for_objective(
        material_id=5,
        objective=objective,
    )

    required = {"Fe", "P", "O"}

    for chain in result["chains"]:
        preserved = set()

        for transition in chain["transitions"]:
            preserved.update(transition["preserved_framework"])

        assert required.issubset(preserved)