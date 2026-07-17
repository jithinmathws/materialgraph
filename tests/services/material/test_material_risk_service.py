from uuid import uuid4

from app.models.element import Element
from app.models.element_risk_profile import ElementRiskProfile
from app.models.material import Material
from app.models.material_element import MaterialElement
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


def test_element_risk_remains_calculable_from_one_available_dimension():
    """Characterize current dimension-level semantics separately from MG-AUD-008."""

    class Profile:
        supply_risk_score = 1.5
        geopolitical_risk_score = None
        toxicity_score = None

    service = MaterialRiskService.__new__(MaterialRiskService)

    assert service._calculate_element_risk(Profile()) == 1.5


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


def test_material_risk_signal_characterizes_partial_element_coverage(db_session):
    """Characterize the upstream partial-coverage signal used by MG-AUD-008."""
    suffix = uuid4().hex[:7]
    symbols = [f"Q{index}{suffix}" for index in range(4)]

    elements = [
        Element(
            symbol=symbol,
            name=f"Characterization element {symbol}",
        )
        for symbol in symbols
    ]
    db_session.add_all(elements)
    db_session.flush()

    material = Material(
        mp_id=f"mp-aud-008-{uuid4().hex}",
        formula="".join(symbols),
        pretty_formula="".join(symbols),
        is_stable=True,
        energy_above_hull=0.0,
        source="audit_characterization",
    )
    db_session.add(material)
    db_session.flush()

    db_session.add_all(
        MaterialElement(
            material_id=material.id,
            element_id=element.id,
            fraction=0.25,
        )
        for element in elements
    )

    db_session.add(
        ElementRiskProfile(
            element_id=elements[0].id,
            year=2026,
            supply_risk_score=1.0,
            geopolitical_risk_score=2.0,
            toxicity_score=1.5,
            source="audit_characterization",
        )
    )
    db_session.flush()

    service = MaterialRiskService(db_session)
    signal = service.get_material_risk_signal(material.id)

    assert signal["material_id"] == material.id
    assert signal["risk_score"] == 1.5
    assert signal["risk_known"] is True
    assert signal["risk_profile_coverage"] == 0.25
    assert signal["known_risk_element_count"] == 1
    assert signal["total_element_count"] == 4
    assert signal["known_risk_elements"] == [symbols[0]]
    assert signal["unknown_risk_elements"] == sorted(symbols[1:])
    assert signal["risk_evidence_complete"] is False


def test_material_risk_signal_scalar_and_bulk_match_for_partial_coverage(db_session):
    """Protect scalar/bulk parity for evidence-aware risk signals."""
    suffix = uuid4().hex[:7]
    symbols = [f"R{index}{suffix}" for index in range(2)]

    elements = [
        Element(symbol=symbol, name=f"Parity element {symbol}")
        for symbol in symbols
    ]
    db_session.add_all(elements)
    db_session.flush()

    material = Material(
        mp_id=f"mp-aud-008-parity-{uuid4().hex}",
        formula="".join(symbols),
        pretty_formula="".join(symbols),
        is_stable=False,
        source="audit_characterization",
    )
    db_session.add(material)
    db_session.flush()

    db_session.add_all(
        MaterialElement(
            material_id=material.id,
            element_id=element.id,
            fraction=0.5,
        )
        for element in elements
    )
    db_session.add(
        ElementRiskProfile(
            element_id=elements[0].id,
            year=2026,
            supply_risk_score=2.0,
            source="audit_characterization",
        )
    )
    db_session.flush()

    service = MaterialRiskService(db_session)

    scalar = service.get_material_risk_signal(material.id)
    bulk = service.get_material_risk_signals_bulk([material.id])[material.id]

    assert scalar == bulk
    assert scalar["risk_profile_coverage"] == 0.5
    assert scalar["risk_evidence_complete"] is False
