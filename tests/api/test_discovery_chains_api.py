def test_get_discovery_chains(client):
    response = client.get(
        "/api/v1/materials/5/discovery/chains"
        "?avoid_element=Li&prefer_element=Na&max_hops=2&limit=5"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 5
    assert "base_formula" in data
    assert "discovery_goal" in data
    assert "chains" in data

    assert data["discovery_goal"]["avoid_element"] == "Li"
    assert data["discovery_goal"]["prefer_element"] == "Na"
    assert data["discovery_goal"]["max_hops"] == 2
    assert data["discovery_goal"]["limit"] == 5

    for chain in data["chains"]:
        assert "materials" in chain
        assert "transitions" in chain
        assert "chain_reason" in chain
        assert chain["hop_count"] <= 2