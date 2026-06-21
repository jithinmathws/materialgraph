from sqlalchemy.orm import Session

from app.models.material import Material
from app.services.discovery_graph_builder import DiscoveryGraphBuilder


class DiscoveryTraversalService:
    DEFAULT_MAX_HOPS = 2
    MAX_ALLOWED_HOPS = 3
    DEFAULT_LIMIT = 50

    def __init__(self, db: Session):
        self.db = db
        self.graph_builder = DiscoveryGraphBuilder(db)

    def get_graph(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
        limit: int = DEFAULT_LIMIT,
    ) -> dict:
        base_material = self.db.get(Material, material_id)

        if base_material is None:
            return self._empty_response(
                material_id=material_id,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                max_hops=max_hops,
                limit=limit,
            )

        graph = self.graph_builder.build_graph(
            start_material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_depth=max_hops,
        )

        return {
            "material_id": base_material.id,
            "mp_id": base_material.mp_id,
            "base_formula": base_material.pretty_formula or base_material.formula,
            "graph_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
                "max_hops": max_hops,
                "limit": limit,
            },
            "nodes": graph["nodes"][:limit],
            "edges": graph["edges"][:limit],
        }

    def get_subgraph(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        family: str | None = None,
        transition_type: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
        limit: int = DEFAULT_LIMIT,
    ) -> dict:
        result = self.get_graph(
            material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_hops=max_hops,
            limit=limit,
        )

        edges = result["edges"]

        if family:
            edges = [
                edge for edge in edges
                if edge["family"] == family
            ]

        if transition_type:
            edges = [
                edge for edge in edges
                if edge["transition_type"] == transition_type
            ]

        connected_ids = set()

        for edge in edges:
            connected_ids.add(edge["source_material_id"])
            connected_ids.add(edge["target_material_id"])

        nodes = [
            node for node in result["nodes"]
            if node["material_id"] in connected_ids
        ]

        result["subgraph_filter"] = {
            "family": family,
            "transition_type": transition_type,
        }
        result["nodes"] = nodes
        result["edges"] = edges[:limit]

        return result

    def get_path(
        self,
        material_id: int,
        target_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
    ) -> dict:
        from app.services.discovery_chain_service import DiscoveryChainService

        chain_service = DiscoveryChainService(self.db)

        result = chain_service.get_discovery_chains(
            material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_hops=max_hops,
            limit=20,
        )

        for chain in result["chains"]:
            material_ids = [
                material["material_id"]
                for material in chain["materials"]
            ]

            if target_material_id in material_ids:
                return {
                    "material_id": material_id,
                    "target_material_id": target_material_id,
                    "path_found": True,
                    "hop_count": chain["hop_count"],
                    "materials": chain["materials"],
                    "transitions": [
                        self._chain_transition_to_graph_edge(transition)
                        for transition in chain["transitions"]
                    ],
                    "path_reason": chain["chain_reason"],
                }

        return {
            "material_id": material_id,
            "target_material_id": target_material_id,
            "path_found": False,
            "hop_count": None,
            "materials": [],
            "transitions": [],
            "path_reason": None,
        }

    def _build_path_reason(self, transitions: list[dict]) -> str:
        if not transitions:
            return "No discovery path was generated."

        transition_types = [
            transition["transition_type"]
            for transition in transitions
        ]

        preserved_frameworks = [
            set(transition["preserved_framework"])
            for transition in transitions
            if transition["preserved_framework"]
        ]

        common_framework = sorted(
            set.intersection(*preserved_frameworks)
            if preserved_frameworks
            else set()
        )

        reason = "This discovery path follows " + " → ".join(transition_types)

        if common_framework:
            reason += f" while preserving {'-'.join(common_framework)} chemistry"

        return reason + "."

    def _empty_response(
        self,
        material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
        max_hops: int,
        limit: int,
    ) -> dict:
        return {
            "material_id": material_id,
            "mp_id": None,
            "base_formula": None,
            "graph_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
                "max_hops": max_hops,
                "limit": limit,
            },
            "nodes": [],
            "edges": [],
        }

    def _chain_transition_to_graph_edge(self, transition: dict) -> dict:
        return {
            "source_material_id": transition["from_material_id"],
            "target_material_id": transition["to_material_id"],
            "transition_type": transition["transition_type"],
            "family": transition.get("family"),
            "preserved_framework": transition.get("preserved_framework", []),
            "removed_elements": transition.get("removed_elements", []),
            "introduced_elements": transition.get("introduced_elements", []),
            "scientific_reason": transition.get("reason")
            or "Scientific transition identified by deterministic chain rules.",
        }