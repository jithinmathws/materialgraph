def test_scientific_pathway_analysis_endpoint(client):
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

    assert data["material_id"] == 5
    assert data["researcher_decision_required"] is True
    assert "pathway_opportunities" in data
    assert "pathway_comparison" in data

    opportunity = data["pathway_opportunities"][0]

    assert opportunity["researcher_decision_required"] is True
    assert "scientific_facts" in opportunity
    assert "quality_summary" in opportunity
    assert "confidence" in opportunity


def test_scientific_pathway_analysis_endpoint_validates_body(client):
    response = client.post(
        "/api/v1/materials/5/research/scientific-pathways",
        json={
            "objective": {
                "max_hops": 99,
                "limit": 5,
            }
        },
    )

    assert response.status_code == 422