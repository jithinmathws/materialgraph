from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.element_risk_profile import ElementRiskProfile
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.schemas.material_risk import ElementRiskSummary, MaterialRiskRead


class MaterialRiskService:
    def __init__(self, db: Session):
        self.db = db

    def get_material_risk(
        self,
        material_id: int,
    ) -> MaterialRiskRead | None:
        material = (
            self.db.query(Material)
            .filter(Material.id == material_id)
            .first()
        )

        if material is None:
            return None

        element_rows = (
            self.db.query(Element)
            .join(MaterialElement, Element.id == MaterialElement.element_id)
            .filter(MaterialElement.material_id == material_id)
            .order_by(Element.symbol)
            .all()
        )

        element_risks: list[ElementRiskSummary] = []

        for element in element_rows:
            profile = self._get_latest_profile(element.id)

            if profile is None:
                continue

            risk_score = self._calculate_element_risk(profile)

            element_risks.append(
                ElementRiskSummary(
                    symbol=element.symbol,
                    risk_score=risk_score,
                    supply_risk_score=profile.supply_risk_score,
                    geopolitical_risk_score=profile.geopolitical_risk_score,
                    toxicity_score=profile.toxicity_score,
                )
            )

        if element_risks:
            material_risk_score = sum(
                item.risk_score for item in element_risks
            ) / len(element_risks)
        else:
            material_risk_score = 0.0

        return MaterialRiskRead(
            material_id=material.id,
            formula=material.formula,
            pretty_formula=material.pretty_formula,
            material_risk_score=round(material_risk_score, 3),
            element_risks=element_risks,
        )

    def _get_latest_profile(
        self,
        element_id: int,
    ) -> ElementRiskProfile | None:
        return (
            self.db.query(ElementRiskProfile)
            .filter(ElementRiskProfile.element_id == element_id)
            .order_by(ElementRiskProfile.year.desc())
            .first()
        )

    def _calculate_element_risk(
        self,
        profile: ElementRiskProfile,
    ) -> float:
        values = [
            profile.supply_risk_score,
            profile.geopolitical_risk_score,
            profile.toxicity_score,
        ]

        available_values = [
            value for value in values if value is not None
        ]

        if not available_values:
            return 0.0

        return round(
            sum(available_values) / len(available_values),
            3,
        )

    def get_material_risk_score(
        self,
        material_id: int,
    ) -> float:
        result = self.get_material_risk(material_id)

        if result is None:
            return 0.0

        return result.material_risk_score