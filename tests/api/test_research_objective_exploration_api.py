def test_research_objective_exploration_api(client):
    response = client.post(
        "/api/v1/materials/5/discovery/objective/explore",
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
            },
            "mode": "balanced",
            "limit": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 5
    assert data["mode"] == "balanced"
    assert "ranked_candidates" in data
    assert "chains" in data
    assert "warnings" in data