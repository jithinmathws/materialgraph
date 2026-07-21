def test_get_material_scenario_recommendations(client):
    response = client.get(
        "/api/v1/materials/5/recommendations/scenario"
        "?element=Li&supply_risk_multiplier=1.5"
        "&avoid_element=Co&prefer_element=Na&limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 5
    assert "mp_id" in data
    assert "pretty_formula" in data
    assert "formula" in data
    assert "criticality_score" in data
    assert "scenario" in data
    assert "recommendations" in data

    assert data["scenario"]["element"] == "Li"
    assert data["scenario"]["supply_risk_multiplier"] == 1.5
    assert data["scenario"]["avoid_element"] == "Co"
    assert data["scenario"]["prefer_element"] == "Na"
    assert data["scenario"]["limit"] == 5

    assert isinstance(data["recommendations"], list)
    assert len(data["recommendations"]) <= 5

    if data["recommendations"]:
        item = data["recommendations"][0]

        assert "material_id" in item
        assert "mp_id" in item
        assert "formula" in item
        assert "similarity_score" in item
        assert "criticality_score" in item
        assert "recommendation_score" in item
        assert "scenario_score" in item
        assert "scenario_delta" in item
        assert "scenario_reason" in item

        assert isinstance(item["scenario_score"], float)
        assert isinstance(item["scenario_delta"], float)
        assert isinstance(item["scenario_reason"], str)

        assert any(
            "supply risk multiplier" in rec["scenario_reason"]
            for rec in data["recommendations"]
        )

        for recommendation in data["recommendations"]:
            scenario_delta = recommendation["scenario_delta"]
            scenario_reason = recommendation["scenario_reason"]

            assert scenario_delta == round(
                recommendation["scenario_score"]
                - recommendation["recommendation_score"],
                2,
            )

            if scenario_delta > 0:
                assert "final scenario bonus" in scenario_reason
            elif scenario_delta < 0:
                assert "final scenario penalty" in scenario_reason
            else:
                assert "no final scenario adjustment" in scenario_reason


def test_get_material_scenario_recommendations_not_found(client):
    response = client.get(
        "/api/v1/materials/999999/recommendations/scenario"
        "?element=Li&supply_risk_multiplier=1.5&limit=5"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"


def test_get_material_scenario_recommendations_requires_element(client):
    response = client.get(
        "/api/v1/materials/5/recommendations/scenario"
        "?supply_risk_multiplier=1.5&limit=5"
    )

    assert response.status_code == 422