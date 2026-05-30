def test_get_material_risk(client):
    response = client.get("/api/v1/material-risks/6")

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 6
    assert data["material_risk_score"] >= 0
    assert len(data["element_risks"]) > 0


def test_get_material_risk_not_found(client):
    response = client.get("/api/v1/material-risks/999999")

    assert response.status_code == 404