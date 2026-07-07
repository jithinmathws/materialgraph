from app.services.material.risk_service import MaterialRiskService

def test_material_risk_signal_returns_unknown_for_missing_material(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk_signal(999999)

    assert result["risk_score"] is None
    assert result["risk_known"] is False
    assert result["risk_profile_coverage"] == 0.0
    assert result["known_risk_element_count"] == 0
    assert result["risk_evidence_complete"] is False


def test_material_risk_signals_bulk_returns_coverage_metadata(db_session):
    service = MaterialRiskService(db_session)

    result = service.get_material_risk_signals_bulk([5, 6, 7])

    assert set(result.keys()) == {5, 6, 7}

    for signal in result.values():
        assert "risk_score" in signal
        assert "risk_known" in signal
        assert "risk_profile_coverage" in signal
        assert "known_risk_element_count" in signal
        assert "total_element_count" in signal
        assert "known_risk_elements" in signal
        assert "unknown_risk_elements" in signal
        assert "risk_evidence_complete" in signal


def test_element_risk_with_no_values_is_unknown():
    class Profile:
        supply_risk_score = None
        geopolitical_risk_score = None
        toxicity_score = None

    service = MaterialRiskService.__new__(MaterialRiskService)

    assert service._calculate_element_risk(Profile()) is None


def test_unknown_risk_signal_is_explicit():
    service = MaterialRiskService.__new__(MaterialRiskService)

    signal = service._unknown_risk_signal(
        material_id=123,
        total_element_count=2,
        unknown_element_symbols=["Li", "O"],
    )

    assert signal["risk_score"] is None
    assert signal["risk_known"] is False
    assert signal["risk_profile_coverage"] == 0.0
    assert signal["known_risk_element_count"] == 0
    assert signal["total_element_count"] == 2
    assert signal["unknown_risk_elements"] == ["Li", "O"]
    assert signal["risk_evidence_complete"] is False