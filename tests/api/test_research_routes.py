def test_scientific_pathway_analysis_returns_comparative_intelligence(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()
    comparison = data["pathway_comparison"]

    assert comparison["comparison_count"] == len(
        data["pathway_opportunities"]
    )

    assert "top_ranked_pathway" in comparison
    assert "comparative_strengths" in comparison
    assert "comparative_trade_offs" in comparison
    assert "comparative_research_gaps" in comparison
    assert "comparative_evidence_readiness" in comparison
    assert "comparative_assumptions" in comparison

    assert comparison["researcher_decision_required"] is True
    assert comparison["decision_boundary"]

    opportunities = data["pathway_opportunities"]

    for expected_position, opportunity in enumerate(
        opportunities,
        start=1,
    ):
        assert opportunity["position"] == expected_position
        assert opportunity["pathway_id"].startswith("pathway:")

def test_scientific_pathway_comparison_top_rank_matches_highest_score(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()
    opportunities = data["pathway_opportunities"]
    comparison = data["pathway_comparison"]

    if not opportunities:
        assert comparison["top_ranking_status"] == "unavailable"
        assert comparison["top_score"] is None
        assert comparison["top_ranked_pathway"] is None
        assert comparison["top_ranked_pathways"] == []
        return

    top_score = max(
        opportunity["scientific_usefulness_score"]
        for opportunity in opportunities
    )

    expected_top_group = [
        opportunity
        for opportunity in opportunities
        if opportunity["scientific_usefulness_score"] == top_score
    ]

    assert comparison["top_score"] == top_score

    if len(expected_top_group) == 1:
        assert comparison["top_ranking_status"] == "unique"
        assert comparison["top_ranked_pathway"] is not None

        expected_top = expected_top_group[0]
        actual_top = comparison["top_ranked_pathway"]

        assert actual_top["pathway_id"] == expected_top["pathway_id"]
        assert actual_top["position"] == expected_top["position"]
        assert actual_top["rank"] == expected_top["rank"]
        assert (
            actual_top["scientific_usefulness_score"]
            == expected_top["scientific_usefulness_score"]
        )

        assert len(comparison["top_ranked_pathways"]) == 1

    else:
        assert comparison["top_ranking_status"] == "tie"
        assert comparison["top_ranked_pathway"] is None

        actual_top_group = comparison["top_ranked_pathways"]

        assert len(actual_top_group) == len(expected_top_group)

        assert all(
            pathway["scientific_usefulness_score"] == top_score
            for pathway in actual_top_group
        )

        assert {
            pathway["rank"]
            for pathway in actual_top_group
        } == {
            pathway["rank"]
            for pathway in expected_top_group
        }

        assert {
            pathway["pathway_id"]
            for pathway in actual_top_group
        } == {
            pathway["pathway_id"]
            for pathway in expected_top_group
        }

        assert {
            pathway["position"]
            for pathway in actual_top_group
        } == {
            pathway["position"]
            for pathway in expected_top_group
        }

        assert len({
            pathway["pathway_id"]
            for pathway in actual_top_group
        }) == len(actual_top_group)

def test_scientific_pathway_comparison_preserves_researcher_autonomy(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    comparison = response.json()["pathway_comparison"]

    assert comparison["researcher_decision_required"] is True

    decision_boundary = comparison["decision_boundary"].lower()

    assert "researchers remain responsible" in decision_boundary
    assert "validation" in decision_boundary

def test_scientific_pathway_analysis_returns_pairwise_comparisons(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()
    opportunities = data["pathway_opportunities"]
    pairwise = data["pathway_comparison"]["pairwise_comparisons"]

    expected_count = max(len(opportunities) - 1, 0)

    assert len(pairwise) == expected_count

    if len(opportunities) < 2:
        return

    first = pairwise[0]

    assert "first_pathway_id" in first
    assert "second_pathway_id" in first
    assert "first_pathway_position" in first
    assert "second_pathway_position" in first
    assert "first_pathway_rank" in first
    assert "second_pathway_rank" in first
    assert "higher_ranked_pathway_rank" in first
    assert "lower_ranked_pathway_rank" in first
    assert "score_difference" in first
    assert "why_higher_ranked" in first
    assert "lower_ranked_pathway_advantages" in first
    assert "evidence_readiness_comparison" in first
    
    assert "comparison_type" in first
    assert "tie_reason" in first
    assert "endpoint_material_comparison" in first

    assert first["score_difference"] >= 0
    assert first["first_pathway_id"] == opportunities[0]["pathway_id"]
    assert first["second_pathway_id"] == opportunities[1]["pathway_id"]
    assert first["first_pathway_position"] == opportunities[0]["position"]
    assert first["second_pathway_position"] == opportunities[1]["position"]

def test_scientific_pathway_analysis_returns_comparative_element_highlights(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    highlights = data["pathway_comparison"][
        "comparative_element_highlights"
    ]

    assert isinstance(highlights, list)

    for highlight in highlights:
        assert "element" in highlight
        assert "role" in highlight
        assert "pathway_ids" in highlight
        assert "pathway_count" in highlight
        assert "appears_in_pathway_ranks" in highlight
        assert "potential_signal" in highlight
        assert "researcher_action" in highlight
        assert highlight["pathway_count"] == len(
            highlight["pathway_ids"]
        )
        assert highlight["requires_validation"] is True

def test_comparative_element_highlights_are_grounded_in_pathway_facts(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()

    opportunities = data["pathway_opportunities"]
    highlights = data["pathway_comparison"][
        "comparative_element_highlights"
    ]

    role_to_fact_key = {
        "introduced_element": "introduced_elements",
        "removed_element": "removed_elements",
        "preserved_framework": "preserved_framework",
    }

    for highlight in highlights:
        fact_key = role_to_fact_key[highlight["role"]]

        grounded_ranks = {
            opportunity["rank"]
            for opportunity in opportunities
            if highlight["element"]
            in opportunity["scientific_facts"].get(fact_key, [])
        }

        assert grounded_ranks == set(
            highlight["appears_in_pathway_ranks"]
        )


def test_scientific_pathway_ties_expose_distinct_pathway_identity(
    client,
):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "avoid_elements": ["Li"],
                "prefer_elements": ["Na"],
                "preserve_elements": ["Fe", "P", "O"],
                "target_family": "phosphate",
                "max_hops": 2,
                "limit": 5,
                "prefer_lower_criticality": True,
                "require_stable_materials": False,
            }
        },
    )

    assert response.status_code == 200

    data = response.json()
    opportunities = data["pathway_opportunities"]
    comparison = data["pathway_comparison"]

    pathway_ids = [
        opportunity["pathway_id"]
        for opportunity in opportunities
    ]
    positions = [
        opportunity["position"]
        for opportunity in opportunities
    ]

    assert len(pathway_ids) == len(set(pathway_ids))
    assert positions == list(range(1, len(opportunities) + 1))

    if comparison["top_ranking_status"] != "tie":
        return

    top_pathways = comparison["top_ranked_pathways"]

    assert len({
        pathway["pathway_id"]
        for pathway in top_pathways
    }) == len(top_pathways)

    assert all(
        pathway["rank"] == top_pathways[0]["rank"]
        for pathway in top_pathways
    )
