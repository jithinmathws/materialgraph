from app.schemas.sensitivity import SensitivityAnalysisRequest
from app.services.sensitivity_analysis_service import SensitivityAnalysisService


def test_sensitivity_analysis_returns_result(db_session):
    service = SensitivityAnalysisService(db_session)

    result = service.analyze(
        SensitivityAnalysisRequest(material_id=6)
    )

    assert result is not None
    assert result.material_id == 6
    assert result.baseline_score >= 0
    assert result.baseline_material_risk_score >= 0
    assert len(result.scenarios) == 4


def test_sensitivity_analysis_returns_none_for_missing_material(db_session):
    service = SensitivityAnalysisService(db_session)

    result = service.analyze(
        SensitivityAnalysisRequest(material_id=999999)
    )

    assert result is None