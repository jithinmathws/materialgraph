def test_k_best_path_service_returns_paths(db_session):
    from app.services.discovery_k_best_path_service import DiscoveryKBestPathService

    service = DiscoveryKBestPathService(db_session)

    result = service.get_k_best_paths(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        k=3,
    )

    assert result["start_material_id"] == 5
    assert result["target_material_id"] == 7
    assert result["k"] == 3
    assert "paths" in result
    assert isinstance(result["paths"], list)


def test_k_best_paths_are_ranked_by_scientific_usefulness(db_session):
    from app.services.discovery_k_best_path_service import DiscoveryKBestPathService

    service = DiscoveryKBestPathService(db_session)

    result = service.get_k_best_paths(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        k=3,
    )

    scores = [
        path["scientific_usefulness_score"]
        for path in result["paths"]
    ]

    assert scores == sorted(scores, reverse=True)


def test_k_best_path_service_respects_k_limit(db_session):
    from app.services.discovery_k_best_path_service import DiscoveryKBestPathService

    service = DiscoveryKBestPathService(db_session)

    result = service.get_k_best_paths(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        k=1,
    )

    assert len(result["paths"]) <= 1