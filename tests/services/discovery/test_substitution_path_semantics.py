from app.services.discovery.substitution_path_service import DiscoverySubstitutionPathService

def test_substitution_path_qualifies_element_overlap():
    result=DiscoverySubstitutionPathService().build_path("LiFePO4","NaFePO4",["Li","Fe","P","O"],["Na","Fe","P","O"],["alkali_substitution"])
    assert result["shared_elements"]==["Fe","O","P"]
    assert result["preserved_framework"]==result["shared_elements"]
    assert result["preservation_basis"]=="element_overlap"
    assert result["structural_preservation_validated"] is False
