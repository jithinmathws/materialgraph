from app.services.discovery.traversal_service import DiscoveryTraversalService

def test_discovery_graph_returns_nodes_and_edges(db_session):
    service = DiscoveryTraversalService(db_session)

    result = service.get_graph(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=50,
    )

    assert result["material_id"] == 5
    assert result["nodes"]
    assert result["edges"]

    edge = result["edges"][0]

    assert "source_material_id" in edge
    assert "target_material_id" in edge
    assert "transition_type" in edge
    assert "preserved_framework" in edge
    assert "removed_elements" in edge
    assert "introduced_elements" in edge
    assert "scientific_reason" in edge


def test_discovery_graph_is_deterministic(db_session):
    service = DiscoveryTraversalService(db_session)

    first = service.get_graph(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=50,
    )

    second = service.get_graph(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=50,
    )

    assert first["nodes"] == second["nodes"]
    assert first["edges"] == second["edges"]


def test_discovery_subgraph_filters_by_family(db_session):
    service = DiscoveryTraversalService(db_session)

    result = service.get_subgraph(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        family="phosphate",
        max_hops=2,
        limit=50,
    )

    assert result["edges"]

    for edge in result["edges"]:
        assert edge["family"] == "phosphate"


def test_discovery_path_returns_path_when_available(db_session):
    service = DiscoveryTraversalService(db_session)

    result = service.get_path(
        material_id=5,
        target_material_id=7,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
    )

    assert "path_found" in result
    assert "materials" in result
    assert "transitions" in result