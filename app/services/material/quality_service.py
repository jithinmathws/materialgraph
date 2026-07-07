from sqlalchemy.orm import Session

from app.models.material import Material
from app.services.material.criticality_service import MaterialCriticalityService
from app.services.material.risk_service import MaterialRiskService


class MaterialQualityService:
    QUALITY_SCORE_MAX = 15.0

    def __init__(self, db: Session):
        self.db = db
        self.criticality_service = MaterialCriticalityService(db)
        self.risk_service = MaterialRiskService(db)
        self._quality_cache: dict[int, dict] = {}

    def get_material_quality(self, material_id: int) -> dict:
        if material_id in self._quality_cache:
            return self._quality_cache[material_id]

        material = self.db.get(Material, material_id)

        if material is None:
            quality = self._empty_quality(material_id)
            self._quality_cache[material_id] = quality
            return quality

        criticality = self.criticality_service.get_material_criticality(material_id)
        criticality_score = criticality.get("criticality_score")

        risk_signal = self.risk_service.get_material_risk_signal(material_id)

        quality = self._build_quality_response(
            material=material,
            criticality_score=criticality_score,
            risk_signal=risk_signal,
        )

        self._quality_cache[material_id] = quality
        return quality

    def get_material_quality_bulk(
        self,
        material_ids: list[int],
    ) -> dict[int, dict]:
        unique_ids = list(dict.fromkeys(material_ids))

        if not unique_ids:
            return {}

        missing_ids = [
            material_id
            for material_id in unique_ids
            if material_id not in self._quality_cache
        ]

        if missing_ids:
            materials = (
                self.db.query(Material)
                .filter(Material.id.in_(missing_ids))
                .all()
            )

            materials_by_id = {
                material.id: material
                for material in materials
            }

            criticality_by_id = (
                self.criticality_service.get_material_criticality_bulk(
                    missing_ids
                )
            )

            risk_signals_by_id = (
                self.risk_service.get_material_risk_signals_bulk(
                    missing_ids
                )
            )

            for material_id in missing_ids:
                material = materials_by_id.get(material_id)

                if material is None:
                    self._quality_cache[material_id] = self._empty_quality(
                        material_id
                    )
                    continue

                criticality = criticality_by_id.get(material_id, {})
                criticality_score = criticality.get("criticality_score")
                risk_signal = risk_signals_by_id.get(
                    material_id,
                    self.risk_service._unknown_risk_signal(
                        material_id=material_id,
                        total_element_count=0,
                    ),
                )

                self._quality_cache[material_id] = self._build_quality_response(
                    material=material,
                    criticality_score=criticality_score,
                    risk_signal=risk_signal,
                )

        return {
            material_id: self._quality_cache[material_id]
            for material_id in unique_ids
        }

    def get_material_quality_score(self, material_id: int) -> float:
        return self.get_material_quality(material_id)["quality_score"]

    def _build_quality_response(
        self,
        material: Material,
        criticality_score: float | None,
        risk_signal: dict,
    ) -> dict:
        risk_score = risk_signal.get("risk_score")
        risk_known = risk_signal.get("risk_known", False)

        stability_score = self._calculate_stability_score(
            is_stable=material.is_stable,
            energy_above_hull=material.energy_above_hull,
        )

        quality_score = self._calculate_quality_score(
            is_stable=material.is_stable,
            energy_above_hull=material.energy_above_hull,
            criticality_score=criticality_score,
            risk_score=risk_score,
            risk_known=risk_known,
        )

        return {
            "material_id": material.id,
            "stability_score": stability_score,
            "energy_above_hull": material.energy_above_hull,
            "criticality_score": criticality_score,
            "risk_score": risk_score,
            "risk_known": risk_known,
            "risk_profile_coverage": risk_signal.get("risk_profile_coverage", 0.0),
            "known_risk_element_count": risk_signal.get("known_risk_element_count", 0),
            "total_element_count": risk_signal.get("total_element_count", 0),
            "risk_evidence_complete": risk_signal.get("risk_evidence_complete", False),
            "unknown_risk_elements": risk_signal.get("unknown_risk_elements", []),
            "quality_score": quality_score,
        }

    def _calculate_stability_score(
        self,
        is_stable: bool,
        energy_above_hull: float | None,
    ) -> float:
        score = 0.0

        if is_stable:
            score += 50.0

        if energy_above_hull is not None:
            if energy_above_hull <= 0.01:
                score += 50.0
            elif energy_above_hull <= 0.05:
                score += 35.0
            elif energy_above_hull <= 0.1:
                score += 20.0

        return round(min(score, 100.0), 2)

    def _calculate_quality_score(
        self,
        is_stable: bool,
        energy_above_hull: float | None,
        criticality_score: float | None,
        risk_score: float | None,
        risk_known: bool,
    ) -> float:
        score = 0.0

        if is_stable:
            score += self.QUALITY_SCORE_MAX * 0.35

        if energy_above_hull is not None:
            if energy_above_hull <= 0.01:
                score += self.QUALITY_SCORE_MAX * 0.35
            elif energy_above_hull <= 0.05:
                score += self.QUALITY_SCORE_MAX * 0.25
            elif energy_above_hull <= 0.1:
                score += self.QUALITY_SCORE_MAX * 0.15

        score += self._calculate_risk_quality_score(
            criticality_score=criticality_score,
            risk_score=risk_score,
            risk_known=risk_known,
        )

        return round(min(score, self.QUALITY_SCORE_MAX), 2)

    def _calculate_risk_quality_score(
        self,
        criticality_score: float | None,
        risk_score: float | None,
        risk_known: bool,
    ) -> float:
        score = 0.0

        if criticality_score is not None:
            if criticality_score <= 30:
                score += self.QUALITY_SCORE_MAX * 0.15
            elif criticality_score <= 60:
                score += self.QUALITY_SCORE_MAX * 0.08

        if risk_known and risk_score is not None:
            if risk_score <= 3:
                score += self.QUALITY_SCORE_MAX * 0.15
            elif risk_score <= 6:
                score += self.QUALITY_SCORE_MAX * 0.08

        return score

    def _empty_quality(self, material_id: int) -> dict:
        return {
            "material_id": material_id,
            "stability_score": 0.0,
            "energy_above_hull": None,
            "criticality_score": None,
            "risk_score": None,
            "risk_known": False,
            "risk_profile_coverage": 0.0,
            "known_risk_element_count": 0,
            "total_element_count": 0,
            "risk_evidence_complete": False,
            "unknown_risk_elements": [],
            "quality_score": 0.0,
        }
