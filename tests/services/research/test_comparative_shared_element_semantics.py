from app.services.research.comparative_research_intelligence_service import ComparativeResearchIntelligenceService

def test_comparative_highlights_use_shared_element_semantics():
    opp={"rank":1,"pathway":{"materials":[],"transitions":[]},"scientific_usefulness_score":90.0,"score_breakdown":{},"scientific_facts":{"shared_elements":["Fe"],"preserved_framework":["Fe"],"introduced_elements":[],"removed_elements":[]},"strengths":[],"trade_offs":[],"risks":[],"assumptions":[],"evidence_summary":{"missing_evidence":[],"weak_assumptions":[],"evidence_readiness":"moderate"}}
    h=ComparativeResearchIntelligenceService().compare_opportunities([opp])["comparative_element_highlights"][0]
    assert h["role"] == "preserved_framework"
    assert h["role_semantics"]=="element_overlap"
    assert h["structural_preservation_validated"] is False
