def test_discovery_chains_returns_valid_response(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=5,
    )

    assert result["material_id"] == 5
    assert result["base_formula"] is not None
    assert "chains" in result
    assert isinstance(result["chains"], list)


def test_discovery_chains_respects_max_hops(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=5,
    )

    for chain in result["chains"]:
        assert chain["hop_count"] <= 2
        assert len(chain["transitions"]) <= 2


def test_discovery_chains_avoid_cycles(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=3,
        limit=10,
    )

    for chain in result["chains"]:
        material_ids = [
            material["material_id"]
            for material in chain["materials"]
        ]

        assert len(material_ids) == len(set(material_ids))


def test_discovery_chains_include_transition_reasons(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=5,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=5,
    )

    for chain in result["chains"]:
        for transition in chain["transitions"]:
            assert transition["transition_type"]
            assert transition["reason"]
            assert isinstance(transition["preserved_framework"], list)


def test_discovery_chains_missing_material_returns_empty_response(db_session):
    from app.services.discovery.chain_service import DiscoveryChainService

    service = DiscoveryChainService(db_session)

    result = service.get_discovery_chains(
        material_id=999999,
        avoid_element="Li",
        prefer_element="Na",
        max_hops=2,
        limit=5,
    )

    assert result["material_id"] == 999999
    assert result["mp_id"] is None
    assert result["base_formula"] is None
    assert result["chains"] == []