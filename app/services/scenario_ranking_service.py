from app.schemas.scenario_ranking import ScenarioRankingRequest, ScenarioRankingResult
from app.schemas.screening import CandidateScreeningRequest
from app.services.candidate_screening_service import CandidateScreeningService


SCENARIO_PRESETS = {
    "lithium_supply_shock": {
        "scarce_elements": ["Li"],
        "avoid_elements": ["Co"],
        "require_stable": True,
        "max_energy_above_hull": 0.05,
    },
    "cobalt_avoidance": {
        "scarce_elements": [],
        "avoid_elements": ["Co"],
        "require_stable": True,
        "max_energy_above_hull": 0.05,
    },
    "low_supply_risk": {
        "scarce_elements": ["Li", "Co"],
        "avoid_elements": [],
        "require_stable": True,
        "max_energy_above_hull": 0.05,
    },
}


class ScenarioRankingService:
    def __init__(self, screening_service: CandidateScreeningService):
        self.screening_service = screening_service

    def rank_for_scenario(
        self,
        request: ScenarioRankingRequest,
    ) -> list[ScenarioRankingResult]:
        if request.scenario_name not in SCENARIO_PRESETS:
            raise ValueError(f"Unknown scenario: {request.scenario_name}")

        preset = SCENARIO_PRESETS[request.scenario_name]

        screening_request = CandidateScreeningRequest(**preset)

        results = self.screening_service.screen_candidates(screening_request)

        return [
            ScenarioRankingResult(
                rank=index + 1,
                scenario_name=request.scenario_name,
                material_id=result.material_id,
                mp_id=result.mp_id,
                formula=result.formula,
                pretty_formula=result.pretty_formula,
                score=result.score,
                material_risk_score=result.material_risk_score,
                risk_penalty=result.risk_penalty,
                reasons=result.reasons,
                ranking_explanation=self._build_ranking_explanation(
                    scenario_name=request.scenario_name,
                    result=result,
                ),
            )
            for index, result in enumerate(results[: request.top_n])
        ]

    def _build_ranking_explanation(
        self,
        scenario_name: str,
        result,
    ) -> list[str]:
        explanations = []

        if scenario_name == "lithium_supply_shock":
            if "Li" not in result.elements:
                explanations.append("Candidate avoids lithium dependency")
            else:
                explanations.append("Candidate still depends on lithium")

        if scenario_name == "cobalt_avoidance":
            if "Co" not in result.elements:
                explanations.append("Candidate avoids cobalt")
            else:
                explanations.append("Candidate contains cobalt")

        if result.material_risk_score <= 2:
            explanations.append("Candidate has low aggregate material risk")
        elif result.material_risk_score <= 5:
            explanations.append("Candidate has moderate aggregate material risk")
        else:
            explanations.append("Candidate has high aggregate material risk")

        if result.score >= 60:
            explanations.append("Candidate remains attractive under this scenario")
        elif result.score >= 40:
            explanations.append("Candidate is conditionally attractive")
        else:
            explanations.append("Candidate is weak under this scenario")

        return explanations