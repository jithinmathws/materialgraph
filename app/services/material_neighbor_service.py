from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.material_application import MaterialApplication
from app.models.material_element import MaterialElement


class MaterialNeighborService:
    def __init__(self, db: Session):
        self.db = db

    def get_neighbors(self, material_id: int) -> dict:
        material = self.db.get(Material, material_id)

        if material is None:
            return {
                "material_id": material_id,
                "mp_id": None,
                "pretty_formula": None,
                "formula": None,
                "neighbors": [],
            }

        element_ids = {
            row.element_id
            for row in self.db.query(MaterialElement)
            .filter(MaterialElement.material_id == material_id)
            .all()
        }

        application_ids = {
            row.application_id
            for row in self.db.query(MaterialApplication)
            .filter(MaterialApplication.material_id == material_id)
            .all()
        }

        neighbor_scores: dict[int, dict] = {}

        if element_ids:
            element_neighbors = (
                self.db.query(MaterialElement)
                .filter(MaterialElement.element_id.in_(element_ids))
                .filter(MaterialElement.material_id != material_id)
                .all()
            )

            for row in element_neighbors:
                neighbor_scores.setdefault(
                    row.material_id,
                    {
                        "material_id": row.material_id,
                        "shared_element_count": 0,
                        "shared_application_count": 0,
                        "relationship_types": set(),
                    },
                )

                neighbor_scores[row.material_id]["shared_element_count"] += 1
                neighbor_scores[row.material_id]["relationship_types"].add("SHARED_ELEMENT")

        if application_ids:
            application_neighbors = (
                self.db.query(MaterialApplication)
                .filter(MaterialApplication.application_id.in_(application_ids))
                .filter(MaterialApplication.material_id != material_id)
                .all()
            )

            for row in application_neighbors:
                neighbor_scores.setdefault(
                    row.material_id,
                    {
                        "material_id": row.material_id,
                        "shared_element_count": 0,
                        "shared_application_count": 0,
                        "relationship_types": set(),
                    },
                )

                neighbor_scores[row.material_id]["shared_application_count"] += 1
                neighbor_scores[row.material_id]["relationship_types"].add("SHARED_APPLICATION")

        neighbor_ids = list(neighbor_scores.keys())

        materials_by_id = {}

        if neighbor_ids:
            materials_by_id = {
                item.id: item
                for item in self.db.query(Material)
                .filter(Material.id.in_(neighbor_ids))
                .all()
            }

        neighbors = []

        for neighbor_id, score_data in neighbor_scores.items():
            neighbor = materials_by_id.get(neighbor_id)

            if neighbor is None:
                continue

            neighbor_score = (
                score_data["shared_element_count"] * 2
                + score_data["shared_application_count"] * 3
            )

            neighbors.append(
                {
                    "material_id": neighbor.id,
                    "mp_id": neighbor.mp_id,
                    "pretty_formula": neighbor.pretty_formula,
                    "formula": neighbor.formula,
                    "material_type": neighbor.material_type,
                    "is_stable": neighbor.is_stable,
                    "energy_above_hull": neighbor.energy_above_hull,
                    "shared_element_count": score_data["shared_element_count"],
                    "shared_application_count": score_data["shared_application_count"],
                    "relationship_types": sorted(score_data["relationship_types"]),
                    "neighbor_score": neighbor_score,
                }
            )

        neighbors.sort(
            key=lambda item: (
                item["neighbor_score"],
                item["shared_application_count"],
                item["shared_element_count"],
            ),
            reverse=True,
        )

        return {
            "material_id": material.id,
            "mp_id": material.mp_id,
            "pretty_formula": material.pretty_formula,
            "formula": material.formula,
            "material_type": material.material_type,
            "is_stable": material.is_stable,
            "energy_above_hull": material.energy_above_hull,
            "neighbors": neighbors,
        }