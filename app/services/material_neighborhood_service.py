from sqlalchemy.orm import Session

from app.services.material_neighbor_service import MaterialNeighborService


class MaterialNeighborhoodService:
    def __init__(self, db: Session):
        self.db = db
        self.neighbor_service = MaterialNeighborService(db)

    def get_neighborhood(
        self,
        material_id: int,
        depth: int = 2,
        limit: int = 25,
    ) -> dict:
        root = self.neighbor_service.get_neighbors(material_id)

        if root["mp_id"] is None:
            return {
                "material_id": material_id,
                "mp_id": None,
                "pretty_formula": None,
                "formula": None,
                "depth": depth,
                "nodes": [],
                "edges": [],
            }

        visited: set[int] = {material_id}
        frontier: list[tuple[int, int]] = [(material_id, 0)]

        nodes: dict[int, dict] = {
            material_id: {
                "material_id": root["material_id"],
                "mp_id": root["mp_id"],
                "pretty_formula": root["pretty_formula"],
                "formula": root["formula"],
                "material_type": root["material_type"],
                "is_stable": root["is_stable"],
                "energy_above_hull": root["energy_above_hull"],
                "depth": 0,
                "best_score": 0,
            }
        }

        edges: list[dict] = []

        while frontier:
            current_id, current_depth = frontier.pop(0)

            if current_depth >= depth:
                continue

            current_neighbors = self.neighbor_service.get_neighbors(current_id)

            for neighbor in current_neighbors["neighbors"]:
                neighbor_id = neighbor["material_id"]

                edge = {
                    "source_material_id": current_id,
                    "target_material_id": neighbor_id,
                    "relationship_types": neighbor["relationship_types"],
                    "shared_element_count": neighbor["shared_element_count"],
                    "shared_application_count": neighbor["shared_application_count"],
                    "edge_score": neighbor["neighbor_score"],
                }

                edges.append(edge)

                next_depth = current_depth + 1

                if neighbor_id not in nodes:
                    nodes[neighbor_id] = {
                        "material_id": neighbor_id,
                        "mp_id": neighbor["mp_id"],
                        "pretty_formula": neighbor["pretty_formula"],
                        "formula": neighbor["formula"],
                        "material_type": neighbor["material_type"],
                        "is_stable": neighbor["is_stable"],
                        "energy_above_hull": neighbor["energy_above_hull"],
                        "depth": next_depth,
                        "best_score": neighbor["neighbor_score"],
                    }
                else:
                    nodes[neighbor_id]["best_score"] = max(
                        nodes[neighbor_id]["best_score"],
                        neighbor["neighbor_score"],
                    )

                if neighbor_id not in visited:
                    visited.add(neighbor_id)
                    frontier.append((neighbor_id, next_depth))

        sorted_nodes = sorted(
            nodes.values(),
            key=lambda item: (item["depth"], -item["best_score"], item["material_id"]),
        )

        sorted_edges = sorted(
            edges,
            key=lambda item: item["edge_score"],
            reverse=True,
        )

        return {
            "material_id": root["material_id"],
            "mp_id": root["mp_id"],
            "pretty_formula": root["pretty_formula"],
            "formula": root["formula"],
            "depth": depth,
            "node_count": len(sorted_nodes[:limit]),
            "edge_count": len(sorted_edges[:limit]),
            "nodes": sorted_nodes[:limit],
            "edges": sorted_edges[:limit],
        }