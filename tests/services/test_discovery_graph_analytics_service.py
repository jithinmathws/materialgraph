def test_degree_centrality_returns_results(db_session):
    from app.services.discovery_graph_analytics_service import (
        DiscoveryGraphAnalyticsService,
    )

    service = DiscoveryGraphAnalyticsService(db_session)

    result = service.degree_centrality(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result["algorithm"] == "degree_centrality"
    assert result["material_count"] >= 1
    assert isinstance(result["materials"], list)

    first = result["materials"][0]
    assert "material_id" in first
    assert "degree_centrality" in first


def test_betweenness_centrality_returns_results(db_session):
    from app.services.discovery_graph_analytics_service import (
        DiscoveryGraphAnalyticsService,
    )

    service = DiscoveryGraphAnalyticsService(db_session)

    result = service.betweenness_centrality(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result["algorithm"] == "betweenness_centrality"
    assert result["material_count"] >= 1
    assert isinstance(result["materials"], list)

    first = result["materials"][0]
    assert "material_id" in first
    assert "betweenness_centrality" in first


def test_closeness_centrality_returns_results(db_session):
    from app.services.discovery_graph_analytics_service import (
        DiscoveryGraphAnalyticsService,
    )

    service = DiscoveryGraphAnalyticsService(db_session)

    result = service.closeness_centrality(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result["algorithm"] == "closeness_centrality"
    assert result["material_count"] >= 1
    assert isinstance(result["materials"], list)

    first = result["materials"][0]
    assert "material_id" in first
    assert "closeness_centrality" in first