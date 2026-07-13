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

        return self._build_criticality_response(
            material=material,
            material_element_rows=material_element_rows,
            risk_profiles_by_element_id=risk_profiles_by_element_id,
        )

    def get_material_criticality_bulk(
        self,
        material_ids: list[int],
    ) -> dict[int, dict]:
        unique_ids = list(dict.fromkeys(material_ids))

        if not unique_ids:
            return {}

        materials = (
            self.db.query(Material)
            .filter(Material.id.in_(unique_ids))
            .all()
        )

        materials_by_id = {
            material.id: material
            for material in materials
        }

        material_element_rows = (
            self.db.query(
                MaterialElement,
                Element,
            )
            .join(
                Element,
                MaterialElement.element_id == Element.id,
            )
            .filter(MaterialElement.material_id.in_(unique_ids))
            .all()
        )

        rows_by_material_id: dict[int, list[tuple]] = {}
        element_ids: set[int] = set()

        for material_element, element in material_element_rows:
            rows_by_material_id.setdefault(
                material_element.material_id,
                [],
            ).append((material_element, element))

            element_ids.add(element.id)

        risk_profiles_by_element_id = self._get_latest_risk_profiles(
            element_ids=list(element_ids)
        )

        results: dict[int, dict] = {}

        for material_id in unique_ids:
            material = materials_by_id.get(material_id)

            if material is None:
                results[material_id] = self._empty_criticality_response(
                    material_id
                )
                continue

            results[material_id] = self._build_criticality_response(
                material=material,
                material_element_rows=rows_by_material_id.get(
                    material_id,
                    [],
                ),
                risk_profiles_by_element_id=risk_profiles_by_element_id,
            )

        return results

    def _build_criticality_response(
        self,
        material: Material,
        material_element_rows: list[tuple],
        risk_profiles_by_element_id: dict[int, ElementRiskProfile],
    ) -> dict:
        element_details: list[dict] = []
        weighted_scores: list[float] = []

        total_fraction = 0.0
        known_criticality_fraction = 0.0

        known_criticality_element_count = 0
        unknown_criticality_elements: list[str] = []

        for material_element, element in material_element_rows:
            risk_profile = risk_profiles_by_element_id.get(element.id)

            element_criticality_score = (
                self._calculate_element_criticality_score(risk_profile)
                if risk_profile is not None
                else None
            )

            criticality_known = element_criticality_score is not None
            risk_year = risk_profile.year if risk_profile is not None else None

            fraction = material_element.fraction or 0.0
            total_fraction += fraction

            if criticality_known:
                known_criticality_element_count += 1
                known_criticality_fraction += fraction
                weighted_scores.append(
                    element_criticality_score * fraction
                )
            else:
                unknown_criticality_elements.append(element.symbol)

            element_details.append(
                {
                    "element_id": element.id,
                    "symbol": element.symbol,
                    "name": element.name,
                    "fraction": fraction,
                    "risk_year": risk_year,
                    "abundance_score": (
                        risk_profile.abundance_score
                        if risk_profile
                        else None
                    ),
                    "supply_risk_score": (
                        risk_profile.supply_risk_score
                        if risk_profile
                        else None
                    ),
                    "toxicity_score": (
                        risk_profile.toxicity_score
                        if risk_profile
                        else None
                    ),
                    "recyclability_score": (
                        risk_profile.recyclability_score
                        if risk_profile
                        else None
                    ),
                    "geopolitical_risk_score": (
                        risk_profile.geopolitical_risk_score
                        if risk_profile
                        else None
                    ),
                    "criticality_known": criticality_known,
                    "element_criticality_score": (
                        round(element_criticality_score, 2)
                        if element_criticality_score is not None
                        else None
                    ),
                }
            )

        total_element_count = len(material_element_rows)
        unknown_criticality_element_count = (
            total_element_count - known_criticality_element_count
        )

        criticality_score = self._calculate_material_criticality_score(
            weighted_scores=weighted_scores,
            known_fraction=known_criticality_fraction,
        )

        criticality_known = criticality_score is not None

        criticality_profile_coverage = (
            known_criticality_element_count / total_element_count
            if total_element_count > 0
            else 0.0
        )

        criticality_fraction_coverage = (
            known_criticality_fraction / total_fraction
            if total_fraction > 0
            else 0.0
        )

        unknown_criticality_fraction = max(
            total_fraction - known_criticality_fraction,
            0.0,
        )

        element_details.sort(
            key=lambda item: (
                item["element_criticality_score"] is not None,
                item["element_criticality_score"]
                if item["element_criticality_score"] is not None
                else 0.0,
            ),
            reverse=True,
        )

        return {
            "material_id": material.id,
            "mp_id": material.mp_id,
            "pretty_formula": material.pretty_formula,
            "formula": material.formula,
            "criticality_score": criticality_score,
            "criticality_known": criticality_known,
            "criticality_profile_coverage": round(
                criticality_profile_coverage,
                4,
            ),
            "criticality_fraction_coverage": round(
                criticality_fraction_coverage,
                4,
            ),
            "known_criticality_element_count": (
                known_criticality_element_count
            ),
            "unknown_criticality_element_count": (
                unknown_criticality_element_count
            ),
            "total_element_count": total_element_count,
            "known_criticality_fraction": round(
                known_criticality_fraction,
                6,
            ),
            "unknown_criticality_fraction": round(
                unknown_criticality_fraction,
                6,
            ),
            "criticality_evidence_complete": (
                total_element_count > 0
                and unknown_criticality_element_count == 0
            ),
            "unknown_criticality_elements": sorted(
                unknown_criticality_elements
            ),
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
        known_fraction: float,
    ) -> float | None:
        if known_fraction <= 0:
            return None

        return round(sum(weighted_scores) / known_fraction, 2)

    def _empty_criticality_response(self, material_id: int) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "pretty_formula": None,
            "formula": None,
            "criticality_score": None,
            "criticality_known": False,
            "criticality_profile_coverage": 0.0,
            "criticality_fraction_coverage": 0.0,
            "known_criticality_element_count": 0,
            "unknown_criticality_element_count": 0,
            "total_element_count": 0,
            "known_criticality_fraction": 0.0,
            "unknown_criticality_fraction": 0.0,
            "criticality_evidence_complete": False,
            "unknown_criticality_elements": [],
            "elements": [],
        }

    def _calculate_element_criticality_score(
        self,
        risk_profile: ElementRiskProfile,
    ) -> float | None:
        scores = [
            risk_profile.abundance_score,
            risk_profile.supply_risk_score,
            risk_profile.toxicity_score,
            risk_profile.geopolitical_risk_score,
        ]

        valid_scores = [
            score
            for score in scores
            if score is not None
        ]

        recyclability_score = risk_profile.recyclability_score

        if recyclability_score is not None:
            valid_scores.append(10 - recyclability_score)

        if not valid_scores:
            return None

        return (sum(valid_scores) / len(valid_scores)) * 10