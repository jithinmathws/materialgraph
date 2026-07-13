from types import SimpleNamespace

from app.services.material.criticality_service import (
    MaterialCriticalityService,
)


def _material(
    material_id: int = 1000,
    formula: str = "AB",
):
    return SimpleNamespace(
        id=material_id,
        mp_id=f"test-{material_id}",
        pretty_formula=formula,
        formula=formula,
    )


def _element(
    element_id: int,
    symbol: str,
):
    return SimpleNamespace(
        id=element_id,
        symbol=symbol,
        name=symbol,
    )


def _material_element(
    material_id: int,
    element_id: int,
    fraction: float,
):
    return SimpleNamespace(
        material_id=material_id,
        element_id=element_id,
        fraction=fraction,
    )


def _risk_profile(
    element_id: int,
    *,
    abundance_score=None,
    supply_risk_score=None,
    toxicity_score=None,
    recyclability_score=None,
    geopolitical_risk_score=None,
    year: int = 2026,
):
    return SimpleNamespace(
        element_id=element_id,
        abundance_score=abundance_score,
        supply_risk_score=supply_risk_score,
        toxicity_score=toxicity_score,
        recyclability_score=recyclability_score,
        geopolitical_risk_score=geopolitical_risk_score,
        year=year,
    )


def test_element_without_profile_is_excluded_from_criticality_aggregation():
    service = MaterialCriticalityService.__new__(
        MaterialCriticalityService
    )

    material = _material()
    known_element = _element(1, "A")
    unknown_element = _element(2, "B")

    rows = [
        (
            _material_element(material.id, known_element.id, 0.5),
            known_element,
        ),
        (
            _material_element(material.id, unknown_element.id, 0.5),
            unknown_element,
        ),
    ]

    known_profile = _risk_profile(
        element_id=known_element.id,
        abundance_score=8.0,
        supply_risk_score=8.0,
        toxicity_score=8.0,
        recyclability_score=2.0,
        geopolitical_risk_score=8.0,
    )

    result = service._build_criticality_response(
        material=material,
        material_element_rows=rows,
        risk_profiles_by_element_id={
            known_element.id: known_profile,
        },
    )

    assert result["criticality_score"] == 80.0
    assert result["criticality_known"] is True

    assert result["criticality_profile_coverage"] == 0.5
    assert result["criticality_fraction_coverage"] == 0.5

    assert result["known_criticality_element_count"] == 1
    assert result["unknown_criticality_element_count"] == 1
    assert result["total_element_count"] == 2

    assert result["known_criticality_fraction"] == 0.5
    assert result["unknown_criticality_fraction"] == 0.5

    assert result["criticality_evidence_complete"] is False
    assert result["unknown_criticality_elements"] == ["B"]

    unknown_detail = next(
        item
        for item in result["elements"]
        if item["symbol"] == "B"
    )

    assert unknown_detail["criticality_known"] is False
    assert unknown_detail["element_criticality_score"] is None


def test_all_null_profile_is_unknown_criticality_evidence():
    service = MaterialCriticalityService.__new__(
        MaterialCriticalityService
    )

    material = _material()
    element = _element(1, "A")

    all_null_profile = _risk_profile(
        element_id=element.id,
    )

    result = service._build_criticality_response(
        material=material,
        material_element_rows=[
            (
                _material_element(
                    material.id,
                    element.id,
                    1.0,
                ),
                element,
            )
        ],
        risk_profiles_by_element_id={
            element.id: all_null_profile,
        },
    )

    assert result["criticality_score"] is None
    assert result["criticality_known"] is False
    assert result["criticality_profile_coverage"] == 0.0
    assert result["criticality_fraction_coverage"] == 0.0
    assert result["criticality_evidence_complete"] is False
    assert result["unknown_criticality_elements"] == ["A"]

    assert result["elements"][0]["criticality_known"] is False
    assert (
        result["elements"][0]["element_criticality_score"]
        is None
    )


def test_material_with_no_known_criticality_returns_none():
    service = MaterialCriticalityService.__new__(
        MaterialCriticalityService
    )

    material = _material()
    element_a = _element(1, "A")
    element_b = _element(2, "B")

    result = service._build_criticality_response(
        material=material,
        material_element_rows=[
            (
                _material_element(
                    material.id,
                    element_a.id,
                    0.25,
                ),
                element_a,
            ),
            (
                _material_element(
                    material.id,
                    element_b.id,
                    0.75,
                ),
                element_b,
            ),
        ],
        risk_profiles_by_element_id={},
    )

    assert result["criticality_score"] is None
    assert result["criticality_known"] is False

    assert result["known_criticality_element_count"] == 0
    assert result["unknown_criticality_element_count"] == 2
    assert result["total_element_count"] == 2

    assert result["known_criticality_fraction"] == 0.0
    assert result["unknown_criticality_fraction"] == 1.0

    assert result["criticality_profile_coverage"] == 0.0
    assert result["criticality_fraction_coverage"] == 0.0
    assert result["criticality_evidence_complete"] is False
    assert result["unknown_criticality_elements"] == ["A", "B"]


def test_fully_known_criticality_evidence_is_complete():
    service = MaterialCriticalityService.__new__(
        MaterialCriticalityService
    )

    material = _material()
    element_a = _element(1, "A")
    element_b = _element(2, "B")

    result = service._build_criticality_response(
        material=material,
        material_element_rows=[
            (
                _material_element(
                    material.id,
                    element_a.id,
                    0.25,
                ),
                element_a,
            ),
            (
                _material_element(
                    material.id,
                    element_b.id,
                    0.75,
                ),
                element_b,
            ),
        ],
        risk_profiles_by_element_id={
            element_a.id: _risk_profile(
                element_id=element_a.id,
                abundance_score=4.0,
            ),
            element_b.id: _risk_profile(
                element_id=element_b.id,
                abundance_score=8.0,
            ),
        },
    )

    # (40 × 0.25) + (80 × 0.75) = 70
    assert result["criticality_score"] == 70.0
    assert result["criticality_known"] is True

    assert result["criticality_profile_coverage"] == 1.0
    assert result["criticality_fraction_coverage"] == 1.0
    assert result["criticality_evidence_complete"] is True
    assert result["unknown_criticality_elements"] == []


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

    assert result["criticality_known"] is False
    assert result["criticality_profile_coverage"] == 0.0
    assert result["criticality_fraction_coverage"] == 0.0
    assert result["known_criticality_element_count"] == 0
    assert result["unknown_criticality_element_count"] == 0
    assert result["total_element_count"] == 0
    assert result["criticality_evidence_complete"] is False
    assert result["unknown_criticality_elements"] == []


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

    assert bulk[5] == single


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

    missing = result[999999]

    assert missing["material_id"] == 999999
    assert missing["mp_id"] is None
    assert missing["criticality_score"] is None
    assert missing["criticality_known"] is False
    assert missing["criticality_profile_coverage"] == 0.0
    assert missing["criticality_fraction_coverage"] == 0.0
    assert missing["known_criticality_element_count"] == 0
    assert missing["unknown_criticality_element_count"] == 0
    assert missing["total_element_count"] == 0
    assert missing["known_criticality_fraction"] == 0.0
    assert missing["unknown_criticality_fraction"] == 0.0
    assert missing["criticality_evidence_complete"] is False
    assert missing["unknown_criticality_elements"] == []
    assert missing["elements"] == []