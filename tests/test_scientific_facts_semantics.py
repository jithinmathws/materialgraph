from app.schemas.research_objective_exploration import ScientificFacts

def test_scientific_facts_schema_accepts_shared_element_metadata():
    facts=ScientificFacts(transition_types=["alkali_substitution"],shared_elements=["Fe","O","P"],preserved_framework=["Fe","O","P"],preservation_basis="element_overlap",structural_preservation_validated=False,removed_elements=["Li"],introduced_elements=["Na"],material_quality=[])
    assert facts.shared_elements==facts.preserved_framework
    assert facts.structural_preservation_validated is False
