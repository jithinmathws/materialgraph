def test_scenario_ranking_api(client):
    response = client.post(
        "/api/v1/scenarios/rank",
        json={
            "scenario_name": "lithium_supply_shock",
            "top_n": 5,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) <= 5
    assert len(data) > 0
    assert data[0]["rank"] == 1
    assert data[0]["scenario_name"] == "lithium_supply_shock"
    assert "ranking_explanation" in data[0]


def test_scenario_ranking_api_unknown_scenario(client):
    response = client.post(
        "/api/v1/scenarios/rank",
        json={
            "scenario_name": "unknown_scenario",
            "top_n": 5,
        },
    )

    assert response.status_code == 400