def test_discovery_graph_builder_returns_adjacency(db_session):
    from app.services.discovery_graph_builder import DiscoveryGraphBuilder

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
    from app.services.discovery_graph_builder import DiscoveryGraphBuilder

    builder = DiscoveryGraphBuilder(db_session)

    adjacency = builder.build_adjacency(
        start_material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_depth=0,
    )

    assert adjacency == {}