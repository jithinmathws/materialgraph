from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_materials():
    response = client.get("/api/v1/materials")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_elements():
    response = client.get("/api/v1/elements")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_applications():
    response = client.get("/api/v1/applications")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_element_risk_profiles():
    response = client.get("/api/v1/risks/elements")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_missing_material_returns_404():
    response = client.get("/api/v1/materials/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"