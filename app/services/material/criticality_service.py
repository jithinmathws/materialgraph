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
            return self._empty_criticality_response(material_id)

        material_element_rows = (
            self.db.query(
                MaterialElement,
                Element,
            )
            .join(
                Element,
                MaterialElement.element_id == Element.id,
            )
            .filter(MaterialElement.material_id == material_id)
            .all()
        )

        element_ids = [
            element.id
            for _, element in material_element_rows
        ]

        risk_profiles_by_element_id = self._get_latest_risk_profiles(
            element_ids=element_ids
        )

        element_details = []
        weighted_scores = []
        total_fraction = 0.0

        for material_element, element in material_element_rows:
            risk_profile = risk_profiles_by_element_id.get(element.id)

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
                    "abundance_score": (
                        risk_profile.abundance_score if risk_profile else None
                    ),
                    "supply_risk_score": (
                        risk_profile.supply_risk_score if risk_profile else None
                    ),
                    "toxicity_score": (
                        risk_profile.toxicity_score if risk_profile else None
                    ),
                    "recyclability_score": (
                        risk_profile.recyclability_score if risk_profile else None
                    ),
                    "geopolitical_risk_score": (
                        risk_profile.geopolitical_risk_score
                        if risk_profile
                        else None
                    ),
                    "element_criticality_score": round(
                        element_criticality_score,
                        2,
                    ),
                }
            )

        criticality_score = self._calculate_material_criticality_score(
            weighted_scores=weighted_scores,
            total_fraction=total_fraction,
        )

        element_details.sort(
            key=lambda item: item["element_criticality_score"],
            reverse=True,
        )

        return {
            "material_id": material.id,
            "mp_id": material.mp_id,
            "pretty_formula": material.pretty_formula,
            "formula": material.formula,
            "criticality_score": criticality_score,
            "elements": element_details,
        }

    def _get_latest_risk_profiles(
        self,
        element_ids: list[int],
    ) -> dict[int, ElementRiskProfile]:
        if not element_ids:
            return {}

        risk_profiles = (
            self.db.query(ElementRiskProfile)
            .filter(ElementRiskProfile.element_id.in_(element_ids))
            .order_by(
                ElementRiskProfile.element_id,
                desc(ElementRiskProfile.year),
            )
            .all()
        )

        latest_profiles: dict[int, ElementRiskProfile] = {}

        for risk_profile in risk_profiles:
            if risk_profile.element_id not in latest_profiles:
                latest_profiles[risk_profile.element_id] = risk_profile

        return latest_profiles

    def _calculate_material_criticality_score(
        self,
        weighted_scores: list[float],
        total_fraction: float,
    ) -> float:
        if total_fraction <= 0:
            return 0.0

        return round(sum(weighted_scores) / total_fraction, 2)

    def _empty_criticality_response(self, material_id: int) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "pretty_formula": None,
            "formula": None,
            "criticality_score": None,
            "elements": [],
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