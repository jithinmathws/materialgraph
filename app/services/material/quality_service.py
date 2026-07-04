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

        risk_score = self.risk_service.get_material_risk_score(material_id)

        stability_score = self._calculate_stability_score(
            is_stable=material.is_stable,
            energy_above_hull=material.energy_above_hull,
        )

        quality_score = self._calculate_quality_score(
            is_stable=material.is_stable,
            energy_above_hull=material.energy_above_hull,
            criticality_score=criticality_score,
            risk_score=risk_score,
        )

        quality = {
            "material_id": material.id,
            "stability_score": stability_score,
            "energy_above_hull": material.energy_above_hull,
            "criticality_score": criticality_score,
            "risk_score": risk_score,
            "quality_score": quality_score,
        }

        self._quality_cache[material_id] = quality
        return quality

    def get_material_quality_bulk(
        self,
        material_ids: list[int],
    ) -> dict[int, dict]:
        qualities: dict[int, dict] = {}

        for material_id in dict.fromkeys(material_ids):
            qualities[material_id] = self.get_material_quality(material_id)

        return qualities

    def get_material_quality_score(self, material_id: int) -> float:
        return self.get_material_quality(material_id)["quality_score"]

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
        risk_score: float,
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
        )

        return round(min(score, self.QUALITY_SCORE_MAX), 2)

    def _calculate_risk_quality_score(
        self,
        criticality_score: float | None,
        risk_score: float,
    ) -> float:
        score = 0.0

        if criticality_score is not None:
            if criticality_score <= 30:
                score += self.QUALITY_SCORE_MAX * 0.15
            elif criticality_score <= 60:
                score += self.QUALITY_SCORE_MAX * 0.08

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
            "risk_score": 0.0,
            "quality_score": 0.0,
        }