import heapq
from collections import deque

from sqlalchemy.orm import Session

from app.services.discovery.graph_builder import DiscoveryGraphBuilder


class DiscoveryGraphAlgorithmsService:
    DEFAULT_MAX_DEPTH = 2

    def __init__(self, db: Session):
        self.db = db
        self.graph_builder = DiscoveryGraphBuilder(db)

    def bfs(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        adjacency = self.graph_builder.build_adjacency(
            start_material_id=start_material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_depth=max_depth,
        )

        visited: set[int] = set()
        traversal_order: list[int] = []
        queue = deque([(start_material_id, 0)])

        while queue:
            material_id, depth = queue.popleft()

            if material_id in visited:
                continue

            visited.add(material_id)
            traversal_order.append(material_id)

            if depth >= max_depth:
                continue

            for candidate in adjacency.get(material_id, []):
                candidate_id = candidate["material_id"]

                if candidate_id not in visited:
                    queue.append((candidate_id, depth + 1))

        return {
            "algorithm": "bfs",
            "start_material_id": start_material_id,
            "max_depth": max_depth,
            "visited_count": len(traversal_order),
            "traversal_order": traversal_order,
        }

    def dfs(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        adjacency = self.graph_builder.build_adjacency(
            start_material_id=start_material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_depth=max_depth,
        )

        visited: set[int] = set()
        traversal_order: list[int] = []
        stack: list[tuple[int, int]] = [(start_material_id, 0)]

        while stack:
            material_id, depth = stack.pop()

            if material_id in visited:
                continue

            visited.add(material_id)
            traversal_order.append(material_id)

            if depth >= max_depth:
                continue

            candidates = adjacency.get(material_id, [])

            for candidate in reversed(candidates):
                candidate_id = candidate["material_id"]

                if candidate_id not in visited:
                    stack.append((candidate_id, depth + 1))

        return {
            "algorithm": "dfs",
            "start_material_id": start_material_id,
            "max_depth": max_depth,
            "visited_count": len(traversal_order),
            "traversal_order": traversal_order,
        }

    def shortest_path(
        self,
        start_material_id: int,
        target_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        adjacency = self.graph_builder.build_adjacency(
            start_material_id=start_material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_depth=max_depth,
        )

        queue = deque([(start_material_id, [start_material_id])])
        visited: set[int] = set()

        while queue:
            material_id, path = queue.popleft()

            if material_id == target_material_id:
                return {
                    "algorithm": "shortest_path",
                    "start_material_id": start_material_id,
                    "target_material_id": target_material_id,
                    "path_found": True,
                    "hop_count": len(path) - 1,
                    "path": path,
                }

            if material_id in visited:
                continue

            visited.add(material_id)

            if len(path) - 1 >= max_depth:
                continue

            for candidate in adjacency.get(material_id, []):
                candidate_id = candidate["material_id"]

                if candidate_id not in path:
                    queue.append((candidate_id, [*path, candidate_id]))

        return {
            "algorithm": "shortest_path",
            "start_material_id": start_material_id,
            "target_material_id": target_material_id,
            "path_found": False,
            "hop_count": None,
            "path": [],
        }

    def weighted_shortest_path(
        self,
        start_material_id: int,
        target_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
    ) -> dict:
        graph = self.graph_builder.build_graph(
            start_material_id=start_material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_depth=max_depth,
        )

        nodes_by_id = {
            node["material_id"]: node
            for node in graph["nodes"]
        }

        adjacency = self._build_edge_adjacency(graph["edges"])

        queue = [(0.0, start_material_id, [start_material_id])]
        best_costs: dict[int, float] = {
            start_material_id: 0.0,
        }

        while queue:
            current_cost, material_id, path = heapq.heappop(queue)

            if material_id == target_material_id:
                return {
                    "algorithm": "weighted_shortest_path",
                    "start_material_id": start_material_id,
                    "target_material_id": target_material_id,
                    "path_found": True,
                    "path_cost": round(current_cost, 2),
                    "hop_count": len(path) - 1,
                    "path": path,
                }

            if len(path) - 1 >= max_depth:
                continue

            for edge in adjacency.get(material_id, []):
                next_id = edge["target_material_id"]

                if next_id in path:
                    continue

                edge_cost = self._calculate_edge_cost(
                    edge=edge,
                    target_node=nodes_by_id.get(next_id),
                )

                new_cost = current_cost + edge_cost

                if new_cost < best_costs.get(next_id, float("inf")):
                    best_costs[next_id] = new_cost
                    heapq.heappush(
                        queue,
                        (
                            new_cost,
                            next_id,
                            [*path, next_id],
                        ),
                    )

        return {
            "algorithm": "weighted_shortest_path",
            "start_material_id": start_material_id,
            "target_material_id": target_material_id,
            "path_found": False,
            "path_cost": None,
            "hop_count": None,
            "path": [],
        }

    def _build_edge_adjacency(
        self,
        edges: list[dict],
    ) -> dict[int, list[dict]]:
        adjacency: dict[int, list[dict]] = {}

        for edge in edges:
            source_id = edge["source_material_id"]
            adjacency.setdefault(source_id, []).append(edge)

        return adjacency

    def _calculate_edge_cost(
        self,
        edge: dict,
        target_node: dict | None,
    ) -> float:
        edge_score = edge.get("edge_score") or 0.0
        scientific_plausibility = edge.get("scientific_plausibility") or 0.0

        quality_score = 0.0

        if target_node is not None:
            quality_score = target_node.get("quality_score") or 0.0

        edge_quality = edge_score * 0.7 + (scientific_plausibility * 100) * 0.2 + quality_score * 0.1

        return round(max(1.0, 100.0 - edge_quality), 2)