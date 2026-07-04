def test_classify_family_detects_expected_families(db_session):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    relationships = service._classify_relationships(
        base_elements=["Li", "Fe", "P", "O"],
        candidate_elements=["Na", "Fe", "P", "O"],
    )

    assert "shared_chemistry" in relationships
    assert "alkali_substitution" in relationships
    assert "transition_metal_related" in relationships
    assert "phosphate_related" in relationships
    assert "oxide_related" in relationships