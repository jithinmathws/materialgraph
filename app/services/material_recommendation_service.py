from sqlalchemy.orm import Session

from app.services.material_similarity_service import MaterialSimilarityService


class MaterialRecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.similarity_service = MaterialSimilarityService(db)

    def get_recommendations(
        self,
        material_id: int,
        limit: int = 10,
        prefer_lower_criticality: bool = True,
    ) -> dict:
        similarity_result = self.similarity_service.get_similar_materials(
            material_id=material_id,
            limit=50,
        )

        if similarity_result["mp_id"] is None:
            return {
                "material_id": material_id,
                "mp_id": None,
                "pretty_formula": None,
                "formula": None,
                "criticality_score": None,
                "recommendations": [],
            }

        recommendations = []

        for candidate in similarity_result["similar_materials"]:
            recommendation_score = self._calculate_recommendation_score(
                candidate=candidate,
                prefer_lower_criticality=prefer_lower_criticality,
            )

            recommendations.append(
                {
                    "material_id": candidate["material_id"],
                    "mp_id": candidate["mp_id"],
                    "pretty_formula": candidate["pretty_formula"],
                    "formula": candidate["formula"],
                    "material_type": candidate["material_type"],
                    "is_stable": candidate["is_stable"],
                    "energy_above_hull": candidate["energy_above_hull"],
                    "similarity_score": candidate["similarity_score"],
                    "criticality_score": candidate["criticality_score"],
                    "criticality_delta": candidate["criticality_delta"],
                    "criticality_direction": candidate["criticality_direction"],
                    "shared_element_count": candidate["shared_element_count"],
                    "shared_application_count": candidate["shared_application_count"],
                    "relationship_types": candidate["relationship_types"],
                    "recommendation_score": recommendation_score,
                    "recommendation_reason": self._build_recommendation_reason(
                        candidate=candidate,
                        recommendation_score=recommendation_score,
                    ),
                }
            )

        recommendations.sort(
            key=lambda item: item["recommendation_score"],
            reverse=True,
        )

        return {
            "material_id": similarity_result["material_id"],
            "mp_id": similarity_result["mp_id"],
            "pretty_formula": similarity_result["pretty_formula"],
            "formula": similarity_result["formula"],
            "criticality_score": similarity_result["criticality_score"],
            "recommendations": recommendations[:limit],
        }

    def _calculate_recommendation_score(
        self,
        candidate: dict,
        prefer_lower_criticality: bool,
    ) -> float:
        score = candidate["similarity_score"]

        criticality_delta = candidate["criticality_delta"]

        if prefer_lower_criticality and criticality_delta is not None:
            if criticality_delta < 0:
                score += abs(criticality_delta) * 2
            elif criticality_delta > 0:
                score -= criticality_delta * 2

        if candidate["is_stable"]:
            score += 10

        energy_above_hull = candidate["energy_above_hull"]

        if energy_above_hull is not None and energy_above_hull <= 0.01:
            score += 5

        return round(score, 2)

    def _build_recommendation_reason(
        self,
        candidate: dict,
        recommendation_score: float,
    ) -> str:
        reasons = []

        reasons.append(f"similarity score {candidate['similarity_score']}")

        if candidate["criticality_direction"] == "LOWER_RISK":
            reasons.append(
                f"lower criticality by {abs(candidate['criticality_delta'])}"
            )
        elif candidate["criticality_direction"] == "HIGHER_RISK":
            reasons.append(
                f"higher criticality by {candidate['criticality_delta']}"
            )
        elif candidate["criticality_direction"] == "SAME_RISK":
            reasons.append("same criticality")

        if candidate["shared_element_count"] > 0:
            reasons.append(f"shares {candidate['shared_element_count']} element(s)")

        if candidate["shared_application_count"] > 0:
            reasons.append(f"shares {candidate['shared_application_count']} application(s)")

        if candidate["is_stable"]:
            reasons.append("stable material")

        reasons.append(f"recommendation score {recommendation_score}")

        return "; ".join(reasons)