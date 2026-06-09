def test_get_material_families(client):
    response = client.get("/api/v1/materials/5/families")

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 5
    assert "mp_id" in data
    assert "pretty_formula" in data
    assert "formula" in data
    assert "related_materials" in data
    
    assert isinstance(data["related_materials"], list)

    if data["related_materials"]:
        item = data["related_materials"][0]

        assert "material_id" in item
        assert "mp_id" in item
        assert "pretty_formula" in item
        assert "formula" in item
        assert "relationships" in item
        assert "shared_elements" in item
        assert "relationship_reason" in item

        assert isinstance(item["relationships"], list)
        assert isinstance(item["shared_elements"], list)
        assert isinstance(item["relationship_reason"], str)


def test_get_material_families_not_found(client):
    response = client.get("/api/v1/materials/999999/families")

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"