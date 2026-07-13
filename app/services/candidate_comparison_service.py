from sqlalchemy.orm import Session

from app.schemas.comparison import CandidateComparisonRequest, CandidateComparisonResult
from app.schemas.screening import CandidateScreeningRequest, CandidateScreeningResult
from app.services.candidate_screening_service import CandidateScreeningService


class CandidateComparisonService:
    def __init__(self, db: Session):
        self.db = db
        self.screening_service = CandidateScreeningService(db)

    def compare_candidates(
        self,
        request: CandidateComparisonRequest,
    ) -> CandidateComparisonResult | None:
        screening_request = CandidateScreeningRequest(
            scarce_elements=request.scarce_elements,
            avoid_elements=request.avoid_elements,
            require_stable=request.require_stable,
            max_energy_above_hull=request.max_energy_above_hull,
        )

        screened_candidates = self.screening_service.screen_candidates(
            screening_request
        )

        candidate_by_id = {
            candidate.material_id: candidate
            for candidate in screened_candidates
        }

        material_a = candidate_by_id.get(request.material_a_id)
        material_b = candidate_by_id.get(request.material_b_id)

        if material_a is None or material_b is None:
            return None

        winner = material_a if material_a.score >= material_b.score else material_b
        loser = material_b if winner is material_a else material_a

        reasons = self._build_reasons(
            winner=winner,
            loser=loser,
            scarce_elements=request.scarce_elements,
            avoid_elements=request.avoid_elements,
        )

        return CandidateComparisonResult(
            material_a_id=material_a.material_id,
            material_b_id=material_b.material_id,
            material_a_formula=material_a.pretty_formula,
            material_b_formula=material_b.pretty_formula,
            material_a_score=material_a.score,
            material_b_score=material_b.score,
            material_a_risk_score=material_a.material_risk_score,
            material_b_risk_score=material_b.material_risk_score,
            winner_material_id=winner.material_id,
            winner_formula=winner.pretty_formula,
            score_difference=round(abs(material_a.score - material_b.score), 3),
            reasons=reasons,
        )

    def _build_reasons(
        self,
        winner: CandidateScreeningResult,
        loser: CandidateScreeningResult,
        scarce_elements: list[str],
        avoid_elements: list[str],
    ) -> list[str]:
        reasons = []

        if (
            winner.risk_known
            and loser.risk_known
            and winner.material_risk_score is not None
            and loser.material_risk_score is not None
            and winner.material_risk_score < loser.material_risk_score
        ):
            reasons.append(
                f"{winner.pretty_formula} has a lower material risk score "
                f"({winner.material_risk_score} vs {loser.material_risk_score})"
            )

        if (
            not winner.contains_scarce_elements
            and loser.contains_scarce_elements
            and scarce_elements
        ):
            reasons.append(
                f"{winner.pretty_formula} avoids scarce element(s): "
                f"{', '.join(scarce_elements)}"
            )

        if (
            not winner.contains_avoided_elements
            and loser.contains_avoided_elements
            and avoid_elements
        ):
            reasons.append(
                f"{winner.pretty_formula} avoids excluded element(s): "
                f"{', '.join(avoid_elements)}"
            )

        if winner.score > loser.score:
            reasons.append(
                f"{winner.pretty_formula} has a higher screening score "
                f"({winner.score} vs {loser.score})"
            )

        if not reasons:
            reasons.append(
                "Both candidates are similar under the selected constraints"
            )

        return reasons