from sqlalchemy.orm import Session

from app.services.material_similarity_service import MaterialSimilarityService
from app.utils.chemical_formula import contains_element


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

    def get_scenario_recommendations(
        self,
        material_id: int,
        element: str,
        supply_risk_multiplier: float = 1.0,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        limit: int = 10,
    ) -> dict:
        base_result = self.get_recommendations(
            material_id=material_id,
            limit=50,
            prefer_lower_criticality=True,
        )

        scenario_recommendations = []

        for recommendation in base_result["recommendations"]:
            recommendation_score = recommendation["recommendation_score"]
            criticality_score = recommendation["criticality_score"] or 0
            contains_scenario_element = contains_element(
                recommendation["formula"],
                element,
            )

            contains_avoid_element = (
                avoid_element is not None
                and contains_element(
                    recommendation["formula"],
                    avoid_element,
                )
            )

            contains_prefer_element = (
                prefer_element is not None
                and contains_element(
                    recommendation["formula"],
                    prefer_element,
                )
            )

            avoid_element_penalty = 0
            if contains_avoid_element:
                avoid_element_penalty = 25

            prefer_element_bonus = 0
            if contains_prefer_element:
                prefer_element_bonus = 15

            scenario_penalty = (
                criticality_score
                * (supply_risk_multiplier - 1.0)
            )

            scenario_penalty += avoid_element_penalty

            if contains_scenario_element and supply_risk_multiplier > 1.0:
                element_exposure_penalty = (
                    recommendation_score
                    * 0.15
                    * (supply_risk_multiplier - 1.0)
                )
                scenario_penalty += element_exposure_penalty
            else:
                element_exposure_penalty = 0

            scenario_score = round(
                recommendation_score - scenario_penalty + prefer_element_bonus,
                2,
            )

            scenario_recommendations.append(
                {
                    **recommendation,
                    "scenario_score": scenario_score,
                    "scenario_delta": round(
                        scenario_score - recommendation_score,
                        2,
                    ),
                    "scenario_reason": (
                        f"{element} supply risk multiplier "
                        f"{supply_risk_multiplier} applied; "
                        f"criticality score {criticality_score}; "
                        f"contains {element}: {contains_scenario_element}; "
                        f"element exposure penalty {round(element_exposure_penalty, 2)}; "
                        f"contains avoided element {avoid_element}: "
                        f"{contains_avoid_element}; "
                        f"avoid element penalty {avoid_element_penalty}; "
                        f"contains preferred element {prefer_element}: "
                        f"{contains_prefer_element}; "
                        f"prefer element bonus {prefer_element_bonus}; "
                        f"scenario penalty {round(scenario_penalty, 2)}"
                    ),
                }
            )

        scenario_recommendations.sort(
            key=lambda item: item["scenario_score"],
            reverse=True,
        )

        return {
            "material_id": base_result["material_id"],
            "mp_id": base_result["mp_id"],
            "pretty_formula": base_result["pretty_formula"],
            "formula": base_result["formula"],
            "criticality_score": base_result["criticality_score"],
            "scenario": {
                "element": element,
                "supply_risk_multiplier": supply_risk_multiplier,
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
                "limit": limit,
            },
            "recommendations": scenario_recommendations[:limit],
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