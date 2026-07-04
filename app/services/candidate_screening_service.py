from sqlalchemy.orm import Session
from app.core.logging import logger

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.schemas.screening import CandidateScreeningRequest, CandidateScreeningResult
from app.services.material.risk_service import MaterialRiskService


DEFAULT_SCREENING_WEIGHTS = {
    "base_score": 50,
    "scarce_element_penalty": -30,
    "avoided_element_penalty": -40,
    "stable_bonus": 20,
    "near_stable_bonus": 10,
    "unstable_penalty": -15,
    "risk_penalty_multiplier": 5,
}


class CandidateScreeningService:
    def __init__(self, db: Session):
        self.db = db
        self.weights = DEFAULT_SCREENING_WEIGHTS
        self.material_risk_service = MaterialRiskService(db)

    def screen_candidates(
        self,
        request: CandidateScreeningRequest,
    ) -> list[CandidateScreeningResult]:
        materials = self.db.query(Material).all()

        results = []

        scarce_elements = set(request.scarce_elements)
        avoid_elements = set(request.avoid_elements)

        for material in materials:
            element_symbols = self._get_material_element_symbols(material.id)

            if request.require_stable and not material.is_stable:
                continue

            if (
                request.max_energy_above_hull is not None
                and material.energy_above_hull is not None
                and material.energy_above_hull > request.max_energy_above_hull
            ):
                continue

            score, reasons = self._score_material(
                material=material,
                element_symbols=element_symbols,
                scarce_elements=scarce_elements,
                avoid_elements=avoid_elements,
            )

            material_risk_score = self.material_risk_service.get_material_risk_score(
                material.id
            )

            risk_penalty = (
                material_risk_score * self.weights["risk_penalty_multiplier"]
            )

            score -= risk_penalty

            reasons.append(
                f"Material risk score {material_risk_score} applied as penalty {round(risk_penalty, 3)}"
            )

            score = max(0.0, min(100.0, score))

            results.append(
                CandidateScreeningResult(
                    material_id=material.id,
                    mp_id=material.mp_id,
                    formula=material.formula,
                    pretty_formula=material.pretty_formula,
                    score=round(score, 3),
                    material_risk_score=material_risk_score,
                    risk_penalty=round(risk_penalty, 3),
                    elements=sorted(element_symbols),
                    contains_scarce_elements=bool(
                        element_symbols.intersection(scarce_elements)
                    ),
                    contains_avoided_elements=bool(
                        element_symbols.intersection(avoid_elements)
                    ),
                    reasons=reasons,
                )
            )

        ranked_results = sorted(results, key=lambda item: item.score, reverse=True)

        logger.info(
            "Screened {} candidate materials with scarce_elements={} avoid_elements={}",
            len(ranked_results),
            request.scarce_elements,
            request.avoid_elements,
        )

        return ranked_results

    def _get_material_element_symbols(self, material_id: int) -> set[str]:
        rows = (
            self.db.query(Element.symbol)
            .join(MaterialElement, Element.id == MaterialElement.element_id)
            .filter(MaterialElement.material_id == material_id)
            .all()
        )

        return {row[0] for row in rows}

    def _score_material(
        self,
        material: Material,
        element_symbols: set[str],
        scarce_elements: set[str],
        avoid_elements: set[str],
    ) -> tuple[float, list[str]]:
        score = float(self.weights["base_score"])
        reasons = []

        scarce_hits = element_symbols.intersection(scarce_elements)
        avoid_hits = element_symbols.intersection(avoid_elements)

        if scarce_hits:
            score += self.weights["scarce_element_penalty"]
            reasons.append(
                f"Contains scarce element(s): {', '.join(sorted(scarce_hits))}"
            )
        else:
            reasons.append("Does not contain scarce elements")

        if avoid_hits:
            score += self.weights["avoided_element_penalty"]
            reasons.append(
                f"Contains avoided element(s): {', '.join(sorted(avoid_hits))}"
            )
        else:
            reasons.append("Does not contain avoided elements")

        if material.is_stable:
            score += self.weights["stable_bonus"]
            reasons.append("Material is stable according to Materials Project")
        elif material.energy_above_hull is not None:
            if material.energy_above_hull <= 0.05:
                score += self.weights["near_stable_bonus"]
                reasons.append("Material is near-stable")
            else:
                score += self.weights["unstable_penalty"]
                reasons.append("Material has higher energy above hull")
        else:
            reasons.append("Stability information unavailable")

        return score, reasons