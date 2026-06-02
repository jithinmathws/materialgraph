def test_get_material_neighbors(client):
    response = client.get("/api/v1/materials/1/neighbors")

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 1
    assert "mp_id" in data
    assert "pretty_formula" in data
    assert "formula" in data
    assert "neighbors" in data
    assert isinstance(data["neighbors"], list)


def test_get_material_neighbors_not_found(client):
    response = client.get("/api/v1/materials/999999/neighbors")

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"