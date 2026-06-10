from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_materials():
    response = client.get("/api/v1/materials")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_materials_with_limit_offset():
    response = client.get("/api/v1/materials?limit=5&offset=0")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 5


def test_list_materials_invalid_limit():
    response = client.get("/api/v1/materials?limit=101")

    assert response.status_code == 422


def test_list_materials_invalid_offset():
    response = client.get("/api/v1/materials?offset=-1")

    assert response.status_code == 422


def test_list_elements():
    response = client.get("/api/v1/elements")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_elements_with_limit_offset():
    response = client.get("/api/v1/elements?limit=5&offset=0")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 5


def test_list_elements_invalid_limit():
    response = client.get("/api/v1/elements?limit=101")

    assert response.status_code == 422


def test_list_elements_invalid_offset():
    response = client.get("/api/v1/elements?offset=-1")

    assert response.status_code == 422


def test_list_applications():
    response = client.get("/api/v1/applications")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_applications_with_limit_offset():
    response = client.get("/api/v1/applications?limit=5&offset=0")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 5


def test_list_applications_invalid_limit():
    response = client.get("/api/v1/applications?limit=101")

    assert response.status_code == 422


def test_list_applications_invalid_offset():
    response = client.get("/api/v1/applications?offset=-1")

    assert response.status_code == 422


def test_list_element_risk_profiles():
    response = client.get("/api/v1/risks/elements")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_element_risk_profiles_with_limit_offset():
    response = client.get("/api/v1/risks/elements?limit=5&offset=0")

    assert response.status_code == 200
    data = response.json()

    assert isinstance(data, list)
    assert len(data) <= 5


def test_list_element_risk_profiles_invalid_limit():
    response = client.get("/api/v1/risks/elements?limit=101")

    assert response.status_code == 422


def test_list_element_risk_profiles_invalid_offset():
    response = client.get("/api/v1/risks/elements?offset=-1")

    assert response.status_code == 422


def test_missing_material_returns_404():
    response = client.get("/api/v1/materials/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Material not found"