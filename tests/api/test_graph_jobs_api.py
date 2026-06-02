def test_create_graph_job(client):
    response = client.post(
        "/api/v1/graph-jobs",
        json={
            "job_type": "SIMILARITY_SEARCH",
            "input_json": {
                "material_id": 1,
                "limit": 10,
            },
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["job_type"] == "SIMILARITY_SEARCH"
    assert data["status"] == "PENDING"
    assert data["input_json"]["material_id"] == 1
    assert data["result_json"] is None
    assert data["error_message"] is None
    assert data["started_at"] is None
    assert data["completed_at"] is None
    assert "id" in data


def test_list_graph_jobs(client):
    client.post(
        "/api/v1/graph-jobs",
        json={
            "job_type": "SCENARIO_RANKING",
            "input_json": {"scenario": "lithium_scarcity"},
        },
    )

    response = client.get("/api/v1/graph-jobs")

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert data[0]["status"] == "PENDING"


def test_get_graph_job_by_id(client):
    create_response = client.post(
        "/api/v1/graph-jobs",
        json={
            "job_type": "SUBSTITUTION_ANALYSIS",
            "input_json": {"material": "cobalt"},
        },
    )

    job_id = create_response.json()["id"]

    response = client.get(f"/api/v1/graph-jobs/{job_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == job_id
    assert data["job_type"] == "SUBSTITUTION_ANALYSIS"
    assert data["status"] == "PENDING"


def test_get_graph_job_not_found(client):
    response = client.get(
        "/api/v1/graph-jobs/00000000-0000-0000-0000-000000000000"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Graph job not found"