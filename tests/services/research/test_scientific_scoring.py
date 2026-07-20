from types import SimpleNamespace

from app.services.research.scientific_pathway_analysis_service import (
    ScientificPathwayAnalysisService,
)


class FakeObjectiveService:
    def __init__(self, chains: list[dict]):
        self.chains = chains

    def generate_chains_for_objective(
        self,
        material_id: int,
        objective,
    ) -> dict:
        return {
            "material_id": material_id,
            "base_formula": "LiFePO4",
            "chains": self.chains,
        }


class IdentityEvidenceService:
    def enrich_opportunity(self, opportunity: dict) -> dict:
        return opportunity


class FakeComparativeService:
    def compare_opportunities(
        self,
        opportunities: list[dict],
    ) -> dict:
        return {
            "comparison_count": len(opportunities),
        }


class FakeEndpointRankingService:
    def rank_opportunities(
        self,
        opportunities: list[dict],
    ) -> dict:
        return {
            "ranking_basis": (
                "endpoint_specific_existing_evidence"
            ),
            "groups": [],
        }


def _build_chain(
    *,
    endpoint_material_id: int,
    endpoint_formula: str,
    score: float,
) -> dict:
    return {
        "hop_count": 1,
        "materials": [
            {
                "material_id": 5,
                "mp_id": "mp-19017",
                "formula": "LiFePO4",
                "pretty_formula": "LiFePO4",
            },
            {
                "material_id": endpoint_material_id,
                "mp_id": f"test-{endpoint_material_id}",
                "formula": endpoint_formula,
                "pretty_formula": endpoint_formula,
            },
        ],
        "transitions": [
            {
                "from_material_id": 5,
                "to_material_id": endpoint_material_id,
                "transition_type": "alkali_substitution",
                "preserved_framework": ["Fe", "O", "P"],
                "removed_elements": ["Li"],
                "introduced_elements": ["Na"],
            }
        ],
        "chain_reason": "Test pathway.",
        "scientific_usefulness_score": score,
        "score_breakdown": {
            "framework_preservation": 30.0,
            "objective_alignment": 25.0,
            "transition_plausibility": 18.5,
            "path_efficiency": 7.5,
            "material_quality": 14.65,
        },
    }


def _build_service(
    chains: list[dict],
) -> ScientificPathwayAnalysisService:
    # Avoid constructing database-backed dependencies.
    service = ScientificPathwayAnalysisService.__new__(
        ScientificPathwayAnalysisService
    )

    service.objective_service = FakeObjectiveService(chains)
    service.evidence_service = IdentityEvidenceService()
    service.comparative_service = FakeComparativeService()
    service.endpoint_ranking_service = (
        FakeEndpointRankingService()
    )
    service._quality_cache = {}

    return service


def _objective():
    return SimpleNamespace(
        avoid_elements=["Li"],
        prefer_elements=["Na"],
        preserve_elements=["Fe", "P", "O"],
        target_family="phosphate",
        max_hops=2,
        limit=5,
        prefer_lower_criticality=True,
        require_stable_materials=False,
    )


def test_equal_score_pathways_share_scientific_rank(
    monkeypatch,
):
    chains = [
        _build_chain(
            endpoint_material_id=7,
            endpoint_formula="Na3Fe3(PO4)4",
            score=95.65,
        ),
        _build_chain(
            endpoint_material_id=8,
            endpoint_formula="Na9Fe3P8O29",
            score=95.65,
        ),
        _build_chain(
            endpoint_material_id=10,
            endpoint_formula="NaFePO4",
            score=95.65,
        ),
    ]

    service = _build_service(chains)

    # Avoid database-backed quality calculations.
    monkeypatch.setattr(
        service,
        "_prefetch_material_quality",
        lambda chains: None,
    )
    monkeypatch.setattr(
        service,
        "_material_quality",
        lambda materials: [],
    )

    result = service.analyze(
        material_id=5,
        objective=_objective(),
    )

    opportunities = result["pathway_opportunities"]

    assert [
        opportunity["scientific_usefulness_score"]
        for opportunity in opportunities
    ] == [95.65, 95.65, 95.65]

    assert [
        opportunity["rank"]
        for opportunity in opportunities
    ] == [1, 1, 1]

def test_different_scores_receive_different_scientific_ranks(
    monkeypatch,
):
    chains = [
        _build_chain(
            endpoint_material_id=7,
            endpoint_formula="A",
            score=96.0,
        ),
        _build_chain(
            endpoint_material_id=8,
            endpoint_formula="B",
            score=95.0,
        ),
        _build_chain(
            endpoint_material_id=10,
            endpoint_formula="C",
            score=90.0,
        ),
    ]

    service = _build_service(chains)

    monkeypatch.setattr(
        service,
        "_prefetch_material_quality",
        lambda chains: None,
    )
    monkeypatch.setattr(
        service,
        "_material_quality",
        lambda materials: [],
    )

    result = service.analyze(
        material_id=5,
        objective=_objective(),
    )

    assert [
        opportunity["rank"]
        for opportunity in result["pathway_opportunities"]
    ] == [1, 2, 3]

def test_scientific_pathways_use_competition_ranking(
    monkeypatch,
):
    chains = [
        _build_chain(
            endpoint_material_id=7,
            endpoint_formula="A",
            score=95.65,
        ),
        _build_chain(
            endpoint_material_id=8,
            endpoint_formula="B",
            score=95.65,
        ),
        _build_chain(
            endpoint_material_id=9,
            endpoint_formula="C",
            score=92.0,
        ),
        _build_chain(
            endpoint_material_id=10,
            endpoint_formula="D",
            score=90.0,
        ),
        _build_chain(
            endpoint_material_id=11,
            endpoint_formula="E",
            score=90.0,
        ),
    ]

    service = _build_service(chains)

    monkeypatch.setattr(
        service,
        "_prefetch_material_quality",
        lambda chains: None,
    )
    monkeypatch.setattr(
        service,
        "_material_quality",
        lambda materials: [],
    )

    result = service.analyze(
        material_id=5,
        objective=_objective(),
    )

    assert [
        opportunity["rank"]
        for opportunity in result["pathway_opportunities"]
    ] == [1, 1, 3, 4, 4]


def test_equal_score_pathways_keep_position_but_share_rank(
    monkeypatch,
):
    chains = [
        _build_chain(
            endpoint_material_id=7,
            endpoint_formula="A",
            score=95.65,
        ),
        _build_chain(
            endpoint_material_id=8,
            endpoint_formula="B",
            score=95.65,
        ),
        _build_chain(
            endpoint_material_id=9,
            endpoint_formula="C",
            score=95.65,
        ),
    ]

    service = _build_service(chains)

    monkeypatch.setattr(
        service,
        "_prefetch_material_quality",
        lambda chains: None,
    )
    monkeypatch.setattr(
        service,
        "_material_quality",
        lambda materials: [],
    )

    result = service.analyze(
        material_id=5,
        objective=_objective(),
    )

    opportunities = result["pathway_opportunities"]

    assert [
        opportunity["position"]
        for opportunity in opportunities
    ] == [1, 2, 3]

    assert [
        opportunity["rank"]
        for opportunity in opportunities
    ] == [1, 1, 1]