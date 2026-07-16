from app.services.discovery.chain_service import DiscoveryChainService


def test_next_candidates_does_not_match_n_to_na():
    service = DiscoveryChainService.__new__(DiscoveryChainService)
    service._candidate_cache = {}
    service.EXPANSION_LIMIT = 6
    service._get_family_result = lambda material_id: {
        "related_materials": [
            {
                "material_id": 10,
                "mp_id": "mp-10",
                "pretty_formula": "NaFePO4",
                "formula": "NaFePO4",
            },
            {
                "material_id": 11,
                "mp_id": "mp-11",
                "pretty_formula": "NFeO2",
                "formula": "NFeO2",
            },
        ]
    }

    candidates = service._get_next_candidates(
        material_id=5,
        avoid_element=None,
        prefer_element="N",
        elements_map={
            10: ["Na", "Fe", "P", "O"],
            11: ["N", "Fe", "O"],
        },
    )

    assert [candidate["material_id"] for candidate in candidates] == [11]


def test_next_candidates_does_not_admit_unknown_preferred_membership():
    service = DiscoveryChainService.__new__(DiscoveryChainService)
    service._candidate_cache = {}
    service.EXPANSION_LIMIT = 6
    service._get_family_result = lambda material_id: {
        "related_materials": [
            {
                "material_id": 12,
                "mp_id": "mp-12",
                "pretty_formula": None,
                "formula": "",
            }
        ]
    }

    candidates = service._get_next_candidates(
        material_id=5,
        avoid_element=None,
        prefer_element="Na",
        elements_map={},
    )

    assert candidates == []
