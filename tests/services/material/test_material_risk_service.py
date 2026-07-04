from app.services.material.risk_service import MaterialRiskService


def test_material_risk_returns_result_for_existing_material(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk(6)

    assert result is not None
    assert result.material_id == 6
    assert result.material_risk_score >= 0
    assert len(result.element_risks) > 0


def test_material_risk_returns_none_for_missing_material(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk(999999)

    assert result is None


def test_material_risk_score_returns_zero_for_missing_material(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk_score(999999)

    assert result == 0.0