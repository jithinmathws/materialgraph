from sqlalchemy.orm import Session

from app.services.material_neighbor_service import MaterialNeighborService


class MaterialSimilarityService:
    def __init__(self, db: Session):
        self.db = db
        self.neighbor_service = MaterialNeighborService(db)

    def get_similar_materials(self, material_id: int, limit: int = 10) -> dict:
        neighbor_result = self.neighbor_service.get_neighbors(material_id)

        if neighbor_result["mp_id"] is None:
            return {
                "material_id": material_id,
                "mp_id": None,
                "pretty_formula": None,
                "formula": None,
                "similar_materials": [],
            }

        similar_materials = []

        for neighbor in neighbor_result["neighbors"][:limit]:
            similarity_score = self._calculate_similarity_score(neighbor)

            similar_materials.append(
                {
                    "material_id": neighbor["material_id"],
                    "mp_id": neighbor["mp_id"],
                    "pretty_formula": neighbor["pretty_formula"],
                    "formula": neighbor["formula"],
                    "material_type": neighbor["material_type"],
                    "is_stable": neighbor["is_stable"],
                    "energy_above_hull": neighbor["energy_above_hull"],
                    "shared_element_count": neighbor["shared_element_count"],
                    "shared_application_count": neighbor["shared_application_count"],
                    "relationship_types": neighbor["relationship_types"],
                    "similarity_score": similarity_score,
                    "reason_summary": self._build_reason_summary(neighbor),
                }
            )

        similar_materials.sort(
            key=lambda item: item["similarity_score"],
            reverse=True,
        )

        return {
            "material_id": neighbor_result["material_id"],
            "mp_id": neighbor_result["mp_id"],
            "pretty_formula": neighbor_result["pretty_formula"],
            "formula": neighbor_result["formula"],
            "material_type": neighbor_result["material_type"],
            "is_stable": neighbor_result["is_stable"],
            "energy_above_hull": neighbor_result["energy_above_hull"],
            "similar_materials": similar_materials,
        }

    def _calculate_similarity_score(self, neighbor: dict) -> float:
        score = 0.0

        score += neighbor["shared_element_count"] * 20
        score += neighbor["shared_application_count"] * 30

        if neighbor["is_stable"]:
            score += 10

        energy_above_hull = neighbor["energy_above_hull"]

        if energy_above_hull is not None:
            if energy_above_hull <= 0.01:
                score += 10
            elif energy_above_hull <= 0.05:
                score += 5

        return round(score, 2)

    def _build_reason_summary(self, neighbor: dict) -> str:
        reasons = []

        if neighbor["shared_element_count"] > 0:
            reasons.append(f"shares {neighbor['shared_element_count']} element(s)")

        if neighbor["shared_application_count"] > 0:
            reasons.append(f"shares {neighbor['shared_application_count']} application(s)")

        if neighbor["is_stable"]:
            reasons.append("is stable")

        if neighbor["energy_above_hull"] is not None:
            reasons.append(f"energy above hull: {neighbor['energy_above_hull']}")

        return "; ".join(reasons)