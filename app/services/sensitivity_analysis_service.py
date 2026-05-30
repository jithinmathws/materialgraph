from sqlalchemy.orm import Session

from app.schemas.screening import CandidateScreeningRequest
from app.schemas.sensitivity import (
    SensitivityAnalysisRequest,
    SensitivityAnalysisResult,
    SensitivityScenarioResult,
)
from app.services.candidate_screening_service import CandidateScreeningService


class SensitivityAnalysisService:
    def __init__(self, db: Session):
        self.db = db
        self.screening_service = CandidateScreeningService(db)

    def analyze(
        self,
        request: SensitivityAnalysisRequest,
    ) -> SensitivityAnalysisResult | None:
        baseline_request = CandidateScreeningRequest(
            scarce_elements=["Li"],
            avoid_elements=["Co"],
            require_stable=True,
            max_energy_above_hull=0.05,
        )

        baseline_results = self.screening_service.screen_candidates(
            baseline_request
        )

        baseline = next(
            (
                result
                for result in baseline_results
                if result.material_id == request.material_id
            ),
            None,
        )

        if baseline is None:
            return None

        scenarios = self._build_sensitivity_scenarios(
            baseline_score=baseline.score,
            baseline_risk_score=baseline.material_risk_score,
        )

        max_delta = max(abs(item.score_delta) for item in scenarios)

        return SensitivityAnalysisResult(
            material_id=baseline.material_id,
            formula=baseline.pretty_formula,
            baseline_score=baseline.score,
            baseline_material_risk_score=baseline.material_risk_score,
            sensitivity_level=self._classify_sensitivity(max_delta),
            scenarios=scenarios,
        )

    def _build_sensitivity_scenarios(
        self,
        baseline_score: float,
        baseline_risk_score: float,
    ) -> list[SensitivityScenarioResult]:
        scenario_definitions = [
            ("supply_risk_plus_25_percent", 1.25),
            ("supply_risk_plus_50_percent", 1.50),
            ("geopolitical_risk_plus_25_percent", 1.25),
            ("geopolitical_risk_plus_50_percent", 1.50),
        ]

        results = []

        for name, multiplier in scenario_definitions:
            adjusted_risk = baseline_risk_score * multiplier
            adjusted_penalty = adjusted_risk * 5

            baseline_penalty = baseline_risk_score * 5
            penalty_delta = adjusted_penalty - baseline_penalty

            adjusted_score = max(0.0, baseline_score - penalty_delta)

            results.append(
                SensitivityScenarioResult(
                    scenario=name,
                    adjusted_score=round(adjusted_score, 3),
                    score_delta=round(adjusted_score - baseline_score, 3),
                )
            )

        return results

    def _classify_sensitivity(self, max_delta: float) -> str:
        if max_delta >= 15:
            return "HIGH"
        if max_delta >= 7:
            return "MEDIUM"
        return "LOW"