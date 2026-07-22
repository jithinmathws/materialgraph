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


def test_phosphate_relationship_reason_does_not_claim_shared_framework(
    db_session,
):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    reason = service._build_relationship_reason(
        base_formula="LiFePO4",
        candidate_formula="NaFePO4",
        relationships=["phosphate_related"],
        shared_elements=["Fe", "O", "P"],
        base_elements=["Li", "Fe", "P", "O"],
        candidate_elements=["Na", "Fe", "P", "O"],
    )

    assert "both materials contain phosphorus and oxygen" in reason
    assert "structural framework similarity is not validated" in reason
    assert "shares phosphate framework" not in reason


def test_oxide_relationship_reason_does_not_claim_shared_framework(
    db_session,
):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    reason = service._build_relationship_reason(
        base_formula="LiFeO2",
        candidate_formula="NaFeO2",
        relationships=["oxide_related"],
        shared_elements=["Fe", "O"],
        base_elements=["Li", "Fe", "O"],
        candidate_elements=["Na", "Fe", "O"],
    )

    assert "both materials contain oxygen" in reason
    assert "oxide structure similarity is not validated" in reason
    assert "shares oxide chemistry" not in reason


def test_phosphate_reason_matches_asymmetric_classification_evidence(
    db_session,
):
    from app.services.material.family_service import MaterialFamilyService

    service = MaterialFamilyService(db_session)

    reason = service._build_relationship_reason(
        base_formula="LiP",
        candidate_formula="NaPO",
        relationships=["phosphate_related"],
        shared_elements=["P"],
        base_elements=["Li", "P"],
        candidate_elements=["Na", "P", "O"],
    )

    assert (
        "both materials contain phosphorus, and the candidate contains oxygen"
        in reason
    )
    assert "structural framework similarity is not validated" in reason