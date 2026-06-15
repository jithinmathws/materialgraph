def test_get_discovery_candidates_returns_200(client):
    response = client.get(
        "/api/v1/materials/5/discovery/candidates"
        "?avoid_element=Li&prefer_element=Na&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 5
    assert data["mp_id"] == "mp-19017"
    assert data["base_formula"] == "LiFePO4"
    assert data["discovery_goal"]["avoid_element"] == "Li"
    assert data["discovery_goal"]["prefer_element"] == "Na"
    assert "candidates" in data
    assert isinstance(data["candidates"], list)


def test_get_discovery_candidates_missing_material_returns_404(client):
    response = client.get(
        "/api/v1/materials/999999/discovery/candidates"
        "?avoid_element=Li&prefer_element=Na"
    )

    assert response.status_code == 404


def test_get_discovery_candidates_validates_limit_min(client):
    response = client.get(
        "/api/v1/materials/5/discovery/candidates"
        "?avoid_element=Li&prefer_element=Na&limit=0"
    )

    assert response.status_code == 422


def test_get_discovery_candidates_validates_limit_max(client):
    response = client.get(
        "/api/v1/materials/5/discovery/candidates"
        "?avoid_element=Li&prefer_element=Na&limit=100"
    )

    assert response.status_code == 422


def test_get_discovery_candidates_validates_avoid_element_length(client):
    response = client.get(
        "/api/v1/materials/5/discovery/candidates"
        "?avoid_element=Lithium&prefer_element=Na"
    )

    assert response.status_code == 422


def test_get_discovery_candidates_validates_prefer_element_length(client):
    response = client.get(
        "/api/v1/materials/5/discovery/candidates"
        "?avoid_element=Li&prefer_element=Sodium"
    )

    assert response.status_code == 422


def test_discovery_candidates_include_explanation_and_path(client):
    response = client.get(
        "/api/v1/materials/5/discovery/candidates"
        "?avoid_element=Li&prefer_element=Na&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data["candidates"]) > 0

    candidate = data["candidates"][0]

    assert "material_id" in candidate
    assert "formula" in candidate
    assert "discovery_score" in candidate
    assert "discovery_path" in candidate
    assert "explanation" in candidate

    assert isinstance(candidate["discovery_path"], list)
    assert isinstance(candidate["explanation"], str)
    assert len(candidate["explanation"]) > 0


def test_discovery_candidates_rank_preferred_na_candidates_above_li_candidates(client):
    response = client.get(
        "/api/v1/materials/5/discovery/candidates"
        "?avoid_element=Li&prefer_element=Na&limit=10"
    )

    assert response.status_code == 200

    data = response.json()
    candidates = data["candidates"]

    assert len(candidates) > 0

    top_candidate = candidates[0]

    assert "Na" in top_candidate["formula"]
    assert "Li" not in top_candidate["formula"]
    assert "preferred_element" in top_candidate["discovery_path"]
    assert "avoided_element_removed" in top_candidate["discovery_path"]


def test_discovery_candidates_penalize_avoided_element(client):
    response = client.get(
        "/api/v1/materials/5/discovery/candidates"
        "?avoid_element=Li&prefer_element=Na&limit=10"
    )

    assert response.status_code == 200

    data = response.json()

    li_candidates = [
        candidate
        for candidate in data["candidates"]
        if "Li" in candidate["formula"]
    ]

    if li_candidates:
        candidate = li_candidates[0]

        assert "contains_avoided_element" in candidate["discovery_path"]
        assert "penalized" in candidate["explanation"]