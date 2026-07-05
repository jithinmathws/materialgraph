from app.services.material.criticality_service import MaterialCriticalityService


def test_material_criticality_returns_score(db_session):
    service = MaterialCriticalityService(db_session)

    result = service.get_material_criticality(material_id=5)

    assert result["material_id"] == 5
    assert result["mp_id"] is not None
    assert "criticality_score" in result
    assert "elements" in result
    assert isinstance(result["elements"], list)


def test_material_criticality_missing_material_is_safe(db_session):
    service = MaterialCriticalityService(db_session)

    result = service.get_material_criticality(material_id=999999)

    assert result["material_id"] == 999999
    assert result["mp_id"] is None
    assert result["criticality_score"] is None
    assert result["elements"] == []


def test_material_criticality_bulk_returns_results(db_session):
    service = MaterialCriticalityService(db_session)

    result = service.get_material_criticality_bulk(
        material_ids=[5, 6, 7]
    )

    assert set(result.keys()) == {5, 6, 7}

    assert result[5]["material_id"] == 5
    assert result[6]["material_id"] == 6
    assert result[7]["material_id"] == 7

    assert "criticality_score" in result[5]
    assert "elements" in result[5]


def test_material_criticality_bulk_matches_single_result(db_session):
    service = MaterialCriticalityService(db_session)

    single = service.get_material_criticality(material_id=5)
    bulk = service.get_material_criticality_bulk(
        material_ids=[5]
    )

    assert bulk[5]["material_id"] == single["material_id"]
    assert bulk[5]["mp_id"] == single["mp_id"]
    assert bulk[5]["pretty_formula"] == single["pretty_formula"]
    assert bulk[5]["formula"] == single["formula"]
    assert bulk[5]["criticality_score"] == single["criticality_score"]
    assert bulk[5]["elements"] == single["elements"]


def test_material_criticality_bulk_handles_duplicate_ids(db_session):
    service = MaterialCriticalityService(db_session)

    result = service.get_material_criticality_bulk(
        material_ids=[5, 5, 6]
    )

    assert list(result.keys()) == [5, 6]
    assert result[5]["material_id"] == 5
    assert result[6]["material_id"] == 6


def test_material_criticality_bulk_empty_input_returns_empty_dict(db_session):
    service = MaterialCriticalityService(db_session)

    result = service.get_material_criticality_bulk(material_ids=[])

    assert result == {}


def test_material_criticality_bulk_missing_material_is_safe(db_session):
    service = MaterialCriticalityService(db_session)

    result = service.get_material_criticality_bulk(
        material_ids=[999999]
    )

    assert result[999999]["material_id"] == 999999
    assert result[999999]["mp_id"] is None
    assert result[999999]["criticality_score"] is None
    assert result[999999]["elements"] == []