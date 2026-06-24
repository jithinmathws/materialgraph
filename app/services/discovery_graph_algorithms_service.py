from collections import deque

from sqlalchemy.orm import Session

from app.services.discovery_graph_builder import DiscoveryGraphBuilder


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