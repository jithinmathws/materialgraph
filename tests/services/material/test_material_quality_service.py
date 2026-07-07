def test_material_quality_service_returns_quality_metadata(db_session):
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService(db_session)

    result = service.get_material_quality(5)

    assert result["material_id"] == 5
    assert "stability_score" in result
    assert "energy_above_hull" in result
    assert "criticality_score" in result
    assert "risk_score" in result
    assert "risk_known" in result
    assert "risk_profile_coverage" in result
    assert "known_risk_element_count" in result
    assert "total_element_count" in result
    assert "risk_evidence_complete" in result
    assert "unknown_risk_elements" in result
    assert "quality_score" in result

    assert isinstance(result["stability_score"], float)
    assert result["risk_score"] is None or isinstance(result["risk_score"], float)
    assert isinstance(result["risk_known"], bool)
    assert isinstance(result["risk_profile_coverage"], float)
    assert isinstance(result["quality_score"], float)


def test_material_quality_service_returns_empty_quality_for_missing_material(db_session):
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService(db_session)

    result = service.get_material_quality(999999)

    assert result == {
        "material_id": 999999,
        "stability_score": 0.0,
        "energy_above_hull": None,
        "criticality_score": None,
        "risk_score": None,
        "risk_known": False,
        "risk_profile_coverage": 0.0,
        "known_risk_element_count": 0,
        "total_element_count": 0,
        "risk_evidence_complete": False,
        "unknown_risk_elements": [],
        "quality_score": 0.0,
    }


def test_unknown_risk_does_not_receive_low_risk_quality_bonus():
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService.__new__(MaterialQualityService)
    service.QUALITY_SCORE_MAX = 15.0

    score = service._calculate_quality_score(
        is_stable=True,
        energy_above_hull=0.0,
        criticality_score=31.0,
        risk_score=None,
        risk_known=False,
    )

    assert score == 11.7


def test_known_low_risk_receives_low_risk_quality_bonus():
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService.__new__(MaterialQualityService)
    service.QUALITY_SCORE_MAX = 15.0

    score = service._calculate_quality_score(
        is_stable=True,
        energy_above_hull=0.0,
        criticality_score=31.0,
        risk_score=1.5,
        risk_known=True,
    )

    assert score == 13.95