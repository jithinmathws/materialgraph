from app.services.research.research_evidence_intelligence_service import ResearchEvidenceIntelligenceService

def test_evidence_qualifies_element_overlap_and_structural_uncertainty():
    evidence=ResearchEvidenceIntelligenceService().build_evidence_summary({"score_breakdown":{"framework_preservation":30.0,"objective_alignment":25.0,"transition_plausibility":18.5,"path_efficiency":7.5,"material_quality":14.0},"scientific_facts":{"shared_elements":["Fe","O","P"],"preserved_framework":["Fe","O","P"]},"quality_summary":{"average_quality_score":14.0,"overall_quality":"strong"}})
    signals=evidence["supporting_signals"]
    assert next(x for x in signals if x["derived_from"]=="framework_preservation")["confidence"]=="moderate"
    assert next(x for x in signals if x["derived_from"]=="element_overlap")["confidence"]=="moderate"
    assert any("Structural preservation is not validated" in x["statement"] for x in signals)
