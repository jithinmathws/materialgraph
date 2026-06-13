from sqlalchemy.orm import Session

from app.models.material import Material
from app.models.material_application import MaterialApplication
from app.models.material_element import MaterialElement


class MaterialNeighborService:
    ELEMENT_RELATIONSHIP = "SHARED_ELEMENT"
    APPLICATION_RELATIONSHIP = "SHARED_APPLICATION"

    def __init__(self, db: Session):
        self.db = db

    def get_neighbors(self, material_id: int) -> dict:
        material = self.db.get(Material, material_id)

        if material is None:
            return self._empty_neighbors_response(material_id)

        element_ids = self._get_material_element_ids(material_id)
        application_ids = self._get_material_application_ids(material_id)

        neighbor_scores: dict[int, dict] = {}

        self._collect_element_neighbors(
            material_id=material_id,
            element_ids=element_ids,
            neighbor_scores=neighbor_scores,
        )

        self._collect_application_neighbors(
            material_id=material_id,
            application_ids=application_ids,
            neighbor_scores=neighbor_scores,
        )

        materials_by_id = self._get_materials_by_id(
            material_ids=list(neighbor_scores.keys())
        )

        neighbors = self._build_neighbors(
            neighbor_scores=neighbor_scores,
            materials_by_id=materials_by_id,
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

    def _empty_neighbors_response(self, material_id: int) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "pretty_formula": None,
            "formula": None,
            "material_type": None,
            "is_stable": None,
            "energy_above_hull": None,
            "neighbors": [],
        }

    def _get_material_element_ids(self, material_id: int) -> set[int]:
        return {
            row.element_id
            for row in self.db.query(MaterialElement)
            .filter(MaterialElement.material_id == material_id)
            .all()
        }

    def _get_material_application_ids(self, material_id: int) -> set[int]:
        return {
            row.application_id
            for row in self.db.query(MaterialApplication)
            .filter(MaterialApplication.material_id == material_id)
            .all()
        }

    def _collect_element_neighbors(
        self,
        material_id: int,
        element_ids: set[int],
        neighbor_scores: dict[int, dict],
    ) -> None:
        if not element_ids:
            return

        element_neighbors = (
            self.db.query(MaterialElement)
            .filter(MaterialElement.element_id.in_(element_ids))
            .filter(MaterialElement.material_id != material_id)
            .all()
        )

        for row in element_neighbors:
            score_data = self._get_or_create_score_data(
                material_id=row.material_id,
                neighbor_scores=neighbor_scores,
            )

            score_data["shared_element_count"] += 1
            score_data["relationship_types"].add(self.ELEMENT_RELATIONSHIP)

    def _collect_application_neighbors(
        self,
        material_id: int,
        application_ids: set[int],
        neighbor_scores: dict[int, dict],
    ) -> None:
        if not application_ids:
            return

        application_neighbors = (
            self.db.query(MaterialApplication)
            .filter(MaterialApplication.application_id.in_(application_ids))
            .filter(MaterialApplication.material_id != material_id)
            .all()
        )

        for row in application_neighbors:
            score_data = self._get_or_create_score_data(
                material_id=row.material_id,
                neighbor_scores=neighbor_scores,
            )

            score_data["shared_application_count"] += 1
            score_data["relationship_types"].add(self.APPLICATION_RELATIONSHIP)

    def _get_or_create_score_data(
        self,
        material_id: int,
        neighbor_scores: dict[int, dict],
    ) -> dict:
        return neighbor_scores.setdefault(
            material_id,
            {
                "material_id": material_id,
                "shared_element_count": 0,
                "shared_application_count": 0,
                "relationship_types": set(),
            },
        )

    def _get_materials_by_id(
        self,
        material_ids: list[int],
    ) -> dict[int, Material]:
        if not material_ids:
            return {}

        return {
            item.id: item
            for item in self.db.query(Material)
            .filter(Material.id.in_(material_ids))
            .all()
        }

    def _build_neighbors(
        self,
        neighbor_scores: dict[int, dict],
        materials_by_id: dict[int, Material],
    ) -> list[dict]:
        neighbors = []

        for neighbor_id, score_data in neighbor_scores.items():
            neighbor = materials_by_id.get(neighbor_id)

            if neighbor is None:
                continue

            neighbor_score = self._calculate_neighbor_score(score_data)

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

        return neighbors

    def _calculate_neighbor_score(self, score_data: dict) -> int:
        return (
            score_data["shared_element_count"] * 2
            + score_data["shared_application_count"] * 3
        )