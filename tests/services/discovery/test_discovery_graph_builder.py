from app.services.discovery.graph_builder import DiscoveryGraphBuilder

def test_discovery_graph_builder_returns_adjacency(db_session):
    builder = DiscoveryGraphBuilder(db_session)

    adjacency = builder.build_adjacency(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=2,
    )

    assert isinstance(adjacency, dict)
    assert 5 in adjacency
    assert isinstance(adjacency[5], list)


def test_discovery_graph_builder_respects_depth_zero(db_session):
    builder = DiscoveryGraphBuilder(db_session)

    adjacency = builder.build_adjacency(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=0,
    )

    assert adjacency == {}

def test_discovery_graph_nodes_include_quality_metadata(db_session):
    builder = DiscoveryGraphBuilder(db_session)

    result = builder.build_graph(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=1,
    )

    node = result["nodes"][0]

    assert "stability_score" in node
    assert "energy_above_hull" in node
    assert "criticality_score" in node
    assert "risk_score" in node
    assert "quality_score" in node

def test_discovery_graph_edges_include_edge_intelligence(db_session):
    builder = DiscoveryGraphBuilder(db_session)

    result = builder.build_graph(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=1,
    )

    assert result["edges"]

    edge = result["edges"][0]

    assert "scientific_plausibility" in edge
    assert "edge_score" in edge
    assert isinstance(edge["scientific_plausibility"], float)
    assert isinstance(edge["edge_score"], float)