def test_classify_family_detects_expected_families(db_session):
    from app.services.material_family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    tags = service._classify_family(
        base_elements=["Li", "Fe", "P", "O"],
        candidate_elements=["Na", "Fe", "P", "O"],
    )

    assert "same_element_family" in tags
    assert "alkali_substitution_family" in tags
    assert "transition_metal_family" in tags
    assert "phosphate_family" in tags
    assert "oxide_family" in tags