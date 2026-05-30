from app.schemas.substitution import SubstitutionRequest
from app.services.substitution_analysis_service import SubstitutionAnalysisService


def test_substitution_analysis_returns_candidates(db_session):
    service = SubstitutionAnalysisService(db_session)

    result = service.analyze(
        SubstitutionRequest(material_id=6, top_n=5)
    )

    assert result is not None
    assert result.source_material_id == 6
    assert len(result.substitutes) <= 5
    assert len(result.substitutes) > 0
    assert result.substitutes[0].similarity_score > 0
    assert result.substitutes[0].rank_score > 0


def test_substitution_analysis_returns_none_for_missing_material(db_session):
    service = SubstitutionAnalysisService(db_session)

    result = service.analyze(
        SubstitutionRequest(material_id=999999, top_n=5)
    )

    assert result is None