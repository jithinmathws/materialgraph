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
        material = self.db.get(Material, material_id)

        if material is None:
            return None

        element_rows = (
            self.db.query(Element)
            .join(MaterialElement, Element.id == MaterialElement.element_id)
            .filter(MaterialElement.material_id == material_id)
            .order_by(Element.symbol)
            .all()
        )

        element_ids = [
            element.id
            for element in element_rows
        ]

        profiles_by_element_id = self._get_latest_profiles(element_ids)

        element_risks: list[ElementRiskSummary] = []

        for element in element_rows:
            profile = profiles_by_element_id.get(element.id)

            if profile is None:
                continue

            risk_score = self._calculate_element_risk(profile)

            if risk_score is None:
                continue

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
            # Backward-compatible API behavior.
            #
            # The public MaterialRiskRead schema currently exposes a numeric
            # material_risk_score. Keep this response stable for existing
            # consumers, but do not use this value as proof of low risk in
            # quality scoring. Quality scoring uses get_material_risk_signal().
            material_risk_score = 0.0

        return MaterialRiskRead(
            material_id=material.id,
            formula=material.formula,
            pretty_formula=material.pretty_formula,
            material_risk_score=round(material_risk_score, 3),
            element_risks=element_risks,
        )

    def get_material_risk_signal(
        self,
        material_id: int,
    ) -> dict:
        return self.get_material_risk_signals_bulk([material_id]).get(
            material_id,
            self._unknown_risk_signal(
                material_id=material_id,
                total_element_count=0,
            ),
        )

    def get_material_risk_signals_bulk(
        self,
        material_ids: list[int],
    ) -> dict[int, dict]:
        unique_ids = list(dict.fromkeys(material_ids))

        if not unique_ids:
            return {}

        material_element_rows = (
            self.db.query(
                MaterialElement.material_id,
                Element,
            )
            .join(
                Element,
                MaterialElement.element_id == Element.id,
            )
            .filter(MaterialElement.material_id.in_(unique_ids))
            .order_by(MaterialElement.material_id, Element.symbol)
            .all()
        )

        elements_by_material_id: dict[int, list[Element]] = {}
        element_ids: set[int] = set()

        for material_id, element in material_element_rows:
            elements_by_material_id.setdefault(material_id, []).append(element)
            element_ids.add(element.id)

        profiles_by_element_id = self._get_latest_profiles(
            list(element_ids)
        )

        risk_signals: dict[int, dict] = {}

        for material_id in unique_ids:
            elements = elements_by_material_id.get(material_id, [])
            total_element_count = len(elements)
            element_risk_scores = []
            known_element_symbols = []
            unknown_element_symbols = []

            for element in elements:
                profile = profiles_by_element_id.get(element.id)

                if profile is None:
                    unknown_element_symbols.append(element.symbol)
                    continue

                risk_score = self._calculate_element_risk(profile)

                if risk_score is None:
                    unknown_element_symbols.append(element.symbol)
                    continue

                element_risk_scores.append(risk_score)
                known_element_symbols.append(element.symbol)

            if not element_risk_scores:
                risk_signals[material_id] = self._unknown_risk_signal(
                    material_id=material_id,
                    total_element_count=total_element_count,
                    unknown_element_symbols=unknown_element_symbols,
                )
                continue

            known_count = len(element_risk_scores)
            coverage = (
                round(known_count / total_element_count, 3)
                if total_element_count
                else 0.0
            )

            risk_signals[material_id] = {
                "material_id": material_id,
                "risk_score": round(
                    sum(element_risk_scores) / known_count,
                    3,
                ),
                "risk_known": True,
                "risk_profile_coverage": coverage,
                "known_risk_element_count": known_count,
                "total_element_count": total_element_count,
                "known_risk_elements": sorted(known_element_symbols),
                "unknown_risk_elements": sorted(unknown_element_symbols),
                "risk_evidence_complete": coverage == 1.0,
            }

        return risk_signals

    def get_material_risk_scores_bulk(
        self,
        material_ids: list[int],
    ) -> dict[int, float]:
        risk_signals = self.get_material_risk_signals_bulk(material_ids)

        # Backward-compatible numeric score API.
        #
        # Unknown risk remains 0.0 here only for legacy callers. New ranking and
        # quality logic should use get_material_risk_signals_bulk() so unknown
        # risk is not interpreted as low risk.
        return {
            material_id: (
                signal["risk_score"]
                if signal.get("risk_score") is not None
                else 0.0
            )
            for material_id, signal in risk_signals.items()
        }

    def _get_latest_profile(
        self,
        element_id: int,
    ) -> ElementRiskProfile | None:
        return self._get_latest_profiles([element_id]).get(element_id)

    def _get_latest_profiles(
        self,
        element_ids: list[int],
    ) -> dict[int, ElementRiskProfile]:
        if not element_ids:
            return {}

        profiles = (
            self.db.query(ElementRiskProfile)
            .filter(ElementRiskProfile.element_id.in_(element_ids))
            .order_by(
                ElementRiskProfile.element_id,
                ElementRiskProfile.year.desc(),
            )
            .all()
        )

        latest_profiles: dict[int, ElementRiskProfile] = {}

        for profile in profiles:
            if profile.element_id not in latest_profiles:
                latest_profiles[profile.element_id] = profile

        return latest_profiles

    def _calculate_element_risk(
        self,
        profile: ElementRiskProfile,
    ) -> float | None:
        values = [
            profile.supply_risk_score,
            profile.geopolitical_risk_score,
            profile.toxicity_score,
        ]

        available_values = [
            value for value in values if value is not None
        ]

        if not available_values:
            return None

        return round(
            sum(available_values) / len(available_values),
            3,
        )

    def get_material_risk_score(
        self,
        material_id: int,
    ) -> float:
        signal = self.get_material_risk_signal(material_id)

        # Backward-compatible numeric score API.
        return (
            signal["risk_score"]
            if signal.get("risk_score") is not None
            else 0.0
        )

    def _unknown_risk_signal(
        self,
        material_id: int,
        total_element_count: int,
        unknown_element_symbols: list[str] | None = None,
    ) -> dict:
        return {
            "material_id": material_id,
            "risk_score": None,
            "risk_known": False,
            "risk_profile_coverage": 0.0,
            "known_risk_element_count": 0,
            "total_element_count": total_element_count,
            "known_risk_elements": [],
            "unknown_risk_elements": sorted(unknown_element_symbols or []),
            "risk_evidence_complete": False,
        }
