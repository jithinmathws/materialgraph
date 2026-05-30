from app.schemas.comparison import CandidateComparisonRequest

def test_compare_materials_api(client):
    response = client.post(
        "/api/v1/comparison/materials",
        json={
            "material_a_id": 6,
            "material_b_id": 12,
            "scarce_elements": ["Li"],
            "avoid_elements": ["Co"],
            "require_stable": True,
            "max_energy_above_hull": 0.05,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["winner_material_id"] in {6, 12}
    assert data["score_difference"] >= 0
    assert len(data["reasons"]) > 0


def test_compare_materials_api_not_found(client):
    response = client.post(
        "/api/v1/comparison/materials",
        json={
            "material_a_id": 6,
            "material_b_id": 999999,
            "scarce_elements": ["Li"],
            "avoid_elements": ["Co"],
        },
    )

    assert response.status_code == 404