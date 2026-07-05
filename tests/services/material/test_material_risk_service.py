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

def test_material_risk_score_returns_float(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk_score(material_id=5)

    assert isinstance(result, float)


def test_material_risk_scores_bulk_returns_scores(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk_scores_bulk(
        material_ids=[5, 6, 7]
    )

    assert set(result.keys()) == {5, 6, 7}
    assert isinstance(result[5], float)
    assert isinstance(result[6], float)
    assert isinstance(result[7], float)


def test_material_risk_scores_bulk_matches_single_score(db_session):
    service = MaterialRiskService(db_session)

    single = service.get_material_risk_score(material_id=5)
    bulk = service.get_material_risk_scores_bulk(
        material_ids=[5]
    )

    assert bulk[5] == single


def test_material_risk_scores_bulk_handles_duplicates(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk_scores_bulk(
        material_ids=[5, 5, 6]
    )

    assert list(result.keys()) == [5, 6]


def test_material_risk_scores_bulk_empty_input_returns_empty_dict(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk_scores_bulk([])

    assert result == {}


def test_material_risk_scores_bulk_missing_material_returns_zero(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk_scores_bulk(
        material_ids=[999999]
    )

    assert result[999999] == 0.0