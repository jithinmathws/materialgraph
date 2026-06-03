from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.element_risk_profile import ElementRiskProfile
from app.models.material import Material
from app.models.material_element import MaterialElement


class MaterialCriticalityService:
    def __init__(self, db: Session):
        self.db = db

    def get_material_criticality(self, material_id: int) -> dict:
        material = self.db.get(Material, material_id)

        if material is None:
            return {
                "material_id": material_id,
                "mp_id": None,
                "pretty_formula": None,
                "formula": None,
                "criticality_score": None,
                "elements": [],
            }

        material_elements = (
            self.db.query(MaterialElement)
            .filter(MaterialElement.material_id == material_id)
            .all()
        )

        element_details = []
        weighted_scores = []
        total_fraction = 0.0

        for material_element in material_elements:
            element = self.db.get(Element, material_element.element_id)

            if element is None:
                continue

            risk_profile = (
                self.db.query(ElementRiskProfile)
                .filter(ElementRiskProfile.element_id == element.id)
                .order_by(desc(ElementRiskProfile.year))
                .first()
            )

            if risk_profile is None:
                element_criticality_score = 0.0
                risk_year = None
            else:
                element_criticality_score = self._calculate_element_criticality_score(
                    risk_profile
                )
                risk_year = risk_profile.year

            fraction = material_element.fraction or 0.0
            total_fraction += fraction
            weighted_scores.append(element_criticality_score * fraction)

            element_details.append(
                {
                    "element_id": element.id,
                    "symbol": element.symbol,
                    "name": element.name,
                    "fraction": fraction,
                    "risk_year": risk_year,
                    "abundance_score": risk_profile.abundance_score if risk_profile else None,
                    "supply_risk_score": risk_profile.supply_risk_score if risk_profile else None,
                    "toxicity_score": risk_profile.toxicity_score if risk_profile else None,
                    "recyclability_score": risk_profile.recyclability_score if risk_profile else None,
                    "geopolitical_risk_score": risk_profile.geopolitical_risk_score if risk_profile else None,
                    "element_criticality_score": round(element_criticality_score, 2),
                }
            )

        if total_fraction > 0:
            criticality_score = sum(weighted_scores) / total_fraction
        else:
            criticality_score = 0.0

        element_details.sort(
            key=lambda item: item["element_criticality_score"],
            reverse=True,
        )

        return {
            "material_id": material.id,
            "mp_id": material.mp_id,
            "pretty_formula": material.pretty_formula,
            "formula": material.formula,
            "criticality_score": round(criticality_score, 2),
            "elements": element_details,
        }

    def _calculate_element_criticality_score(
        self,
        risk_profile: ElementRiskProfile,
    ) -> float:
        scores = [
            risk_profile.abundance_score,
            risk_profile.supply_risk_score,
            risk_profile.toxicity_score,
            risk_profile.geopolitical_risk_score,
        ]

        valid_scores = [score for score in scores if score is not None]

        recyclability_score = risk_profile.recyclability_score

        if recyclability_score is not None:
            valid_scores.append(10 - recyclability_score)

        if not valid_scores:
            return 0.0

        return (sum(valid_scores) / len(valid_scores)) * 10