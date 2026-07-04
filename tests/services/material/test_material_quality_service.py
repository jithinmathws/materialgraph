def test_material_quality_service_returns_quality_metadata(db_session):
    from app.services.material.quality_service import MaterialQualityService

    service = MaterialQualityService(db_session)

    result = service.get_material_quality(5)

    assert result["material_id"] == 5
    assert "stability_score" in result
    assert "energy_above_hull" in result
    assert "criticality_score" in result
    assert "risk_score" in result
    assert "quality_score" in result

    assert isinstance(result["stability_score"], float)
    assert isinstance(result["risk_score"], float)
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
        "risk_score": 0.0,
        "quality_score": 0.0,
    }