from app.services.discovery.transition_validator import (
    DiscoveryTransitionValidator,
)


def _materials():
    return (
        {"material_id": 1, "formula": "LiFePO4"},
        {"material_id": 2, "formula": "NaFePO4"},
    )


def test_multi_element_avoidance_rejects_any_newly_introduced_avoided_element():
    validator = DiscoveryTransitionValidator()
    source, target = _materials()

    result = validator.validate_transition(
        from_material=source,
        to_material=target,
        from_elements=["Fe", "O", "P"],
        to_elements=["Co", "Fe", "O", "P"],
        relationships=["shared_chemistry", "phosphate_related"],
        avoid_elements=["Li", "Co"],
        prefer_elements=["Na", "K"],
    )

    assert result is None


def test_multi_element_avoidance_allows_retained_avoided_elements():
    validator = DiscoveryTransitionValidator()
    source, target = _materials()

    result = validator.validate_transition(
        from_material=source,
        to_material=target,
        from_elements=["Co", "Fe", "O", "P"],
        to_elements=["Co", "Fe", "O", "P"],
        relationships=["shared_chemistry", "phosphate_related"],
        avoid_elements=["Li", "Co"],
    )

    assert result is not None


def test_transition_reason_reports_all_introduced_preferred_elements():
    validator = DiscoveryTransitionValidator()
    source, target = _materials()

    result = validator.validate_transition(
        from_material=source,
        to_material=target,
        from_elements=["Fe", "O", "P"],
        to_elements=["Fe", "K", "Na", "O", "P"],
        relationships=["shared_chemistry", "phosphate_related"],
        prefer_elements=["Na", "K"],
    )

    assert result is not None
    assert "K" in result["reason"]
    assert "Na" in result["reason"]


def test_scalar_transition_contract_remains_supported():
    validator = DiscoveryTransitionValidator()
    source, target = _materials()

    result = validator.validate_transition(
        from_material=source,
        to_material=target,
        from_elements=["Li", "Fe", "O", "P"],
        to_elements=["Na", "Fe", "O", "P"],
        relationships=[
            "alkali_substitution",
            "shared_chemistry",
            "phosphate_related",
        ],
        avoid_element="Li",
        prefer_element="Na",
    )

    assert result is not None
    assert "Na" in result["reason"]
