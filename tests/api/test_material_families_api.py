def test_get_material_families(client):
    response = client.get("/api/v1/materials/5/families")

    assert response.status_code == 200

    data = response.json()

    assert data["material_id"] == 5
    assert "mp_id" in data
    assert "pretty_formula" in data
    assert "formula" in data
    assert "families" in data

    assert isinstance(data["families"], dict)

    expected_families = {
        "same_element_family",
        "alkali_substitution_family",
        "transition_metal_family",
        "phosphate_family",
        "oxide_family",
    }

    assert expected_families.issubset(set(data["families"].keys()))


def test_get_material_families_not_found(client):
    response = client.get("/api/v1/materials/999999/families")

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"