def test_bfs_returns_traversal_order(db_session):
    from app.services.discovery_graph_algorithms_service import (
        DiscoveryGraphAlgorithmsService,
    )

    service = DiscoveryGraphAlgorithmsService(db_session)

    result = service.bfs(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=2,
    )

    assert result["algorithm"] == "bfs"
    assert result["start_material_id"] == 5
    assert result["visited_count"] >= 1
    assert result["traversal_order"][0] == 5


def test_dfs_returns_traversal_order(db_session):
    from app.services.discovery_graph_algorithms_service import (
        DiscoveryGraphAlgorithmsService,
    )

    service = DiscoveryGraphAlgorithmsService(db_session)

    result = service.dfs(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=2,
    )

    assert result["algorithm"] == "dfs"
    assert result["start_material_id"] == 5
    assert result["visited_count"] >= 1
    assert result["traversal_order"][0] == 5


def test_shortest_path_returns_response(db_session):
    from app.services.discovery_graph_algorithms_service import (
        DiscoveryGraphAlgorithmsService,
    )

    service = DiscoveryGraphAlgorithmsService(db_session)

    result = service.shortest_path(
        start_material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=2,
    )

    assert result["algorithm"] == "shortest_path"
    assert result["start_material_id"] == 5
    assert result["target_material_id"] == 7
    assert "path_found" in result
    assert "path" in result