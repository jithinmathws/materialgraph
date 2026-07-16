from app.services.discovery.transition_validator import DiscoveryTransitionValidator

def test_transition_exposes_shared_elements_with_legacy_alias():
    service=DiscoveryTransitionValidator()
    result=service.validate_transition(from_material={"material_id":1,"formula":"LiFePO4"},to_material={"material_id":2,"formula":"NaFePO4"},from_elements=["Li","Fe","P","O"],to_elements=["Na","Fe","P","O"],relationships=["alkali_substitution","phosphate_related"],prefer_element="Na")
    assert result["shared_elements"]==["Fe","O","P"]
    assert result["preserved_framework"]==result["shared_elements"]
    assert result["preservation_basis"]=="element_overlap"
    assert result["structural_preservation_validated"] is False
    assert "structural preservation is not validated" in result["reason"]
