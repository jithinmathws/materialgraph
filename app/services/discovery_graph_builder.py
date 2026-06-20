from sqlalchemy.orm import Session

from app.services.discovery_candidate_service import DiscoveryCandidateService


class DiscoveryGraphBuilder:
    EXPANSION_LIMIT = 50

    def __init__(self, db: Session):
        self.db = db
        self.candidate_service = DiscoveryCandidateService(db)

    def build_adjacency(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = 2,
    ) -> dict[int, list[dict]]:
        adjacency: dict[int, list[dict]] = {}
        visited: set[int] = set()
        frontier: list[tuple[int, int]] = [(start_material_id, 0)]

        while frontier:
            material_id, depth = frontier.pop(0)

            if material_id in visited:
                continue

            visited.add(material_id)

            if depth >= max_depth:
                continue

            candidates = self._get_candidates(
                material_id=material_id,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            )

            adjacency[material_id] = candidates

            for candidate in candidates:
                candidate_id = candidate["material_id"]

                if candidate_id not in visited:
                    frontier.append((candidate_id, depth + 1))

        return adjacency

    def _get_candidates(
        self,
        material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> list[dict]:
        result = self.candidate_service.get_discovery_candidates(
            material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            limit=self.EXPANSION_LIMIT,
        )

        return result["candidates"]