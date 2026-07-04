from collections import deque

from sqlalchemy.orm import Session

from app.core.performance import timed_block
from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.discovery.candidate_service import DiscoveryCandidateService
from app.services.discovery.edge_intelligence_service import (
    DiscoveryEdgeIntelligenceService,
)
from app.services.discovery.transition_validator import DiscoveryTransitionValidator
from app.services.material.family_service import MaterialFamilyService
from app.services.material.quality_service import MaterialQualityService


class DiscoveryGraphBuilder:
    EXPANSION_LIMIT = 6
    ANALYTICS_EXPANSION_LIMIT = 6
    DEFAULT_MAX_DEPTH = 2
    MAX_ALLOWED_DEPTH = 1
    MAX_ANALYTICS_DEPTH = 2

    def __init__(self, db: Session):
        self.db = db
        self.candidate_service = DiscoveryCandidateService(db)
        self.family_service = MaterialFamilyService(db)
        self.transition_validator = DiscoveryTransitionValidator()
        self.material_quality_service = MaterialQualityService(db)
        self.edge_intelligence_service = DiscoveryEdgeIntelligenceService()

        self._family_result_cache: dict[int, dict] = {}
        self._relationship_cache: dict[tuple[int, int], list[str]] = {}
        self._quality_cache: dict[int, dict] = {}

    def build_graph(
        self,
        start_material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_depth: int = DEFAULT_MAX_DEPTH,
        analytics_mode: bool = False,
    ) -> dict:
        with timed_block(
            f"DiscoveryGraphBuilder.total start_material_id={start_material_id}"
        ):
            allowed_depth = (
                self.MAX_ANALYTICS_DEPTH
                if analytics_mode
                else self.MAX_ALLOWED_DEPTH
            )

            max_depth = min(max_depth, allowed_depth)

            with timed_block(
                f"DiscoveryGraphBuilder.base_material start_material_id={start_material_id}"
            ):
                base_material = self.db.get(Material, start_material_id)

            if base_material is None:
                return {
                    "nodes": [],
                    "edges": [],
                    "adjacency": {},
                }

            with timed_block("DiscoveryGraphBuilder.elements_map"):
                elements_map = self._get_material_elements_map()

            nodes_by_id: dict[int, dict] = {
                base_material.id: self._material_to_node(base_material)
            }
            edges_by_key: dict[tuple[int, int, str], dict] = {}
            adjacency: dict[int, list[int]] = {}

            visited: set[int] = set()
            queue = deque([(base_material.id, 0)])

            while queue:
                material_id, depth = queue.popleft()

                if material_id in visited:
                    continue

                visited.add(material_id)

                if depth >= max_depth:
                    continue

                with timed_block(
                    f"DiscoveryGraphBuilder.source_load material_id={material_id}"
                ):
                    source_material = self.db.get(Material, material_id)

                if source_material is None:
                    continue

                source_node = self._material_to_node(source_material)
                nodes_by_id[source_material.id] = source_node

                candidate_limit = (
                    self.ANALYTICS_EXPANSION_LIMIT
                    if analytics_mode
                    else self.EXPANSION_LIMIT
                )

                with timed_block(
                    f"DiscoveryGraphBuilder.get_candidates material_id={material_id}"
                ):
                    candidates = self._get_candidates(
                        material_id=material_id,
                        avoid_element=avoid_element,
                        prefer_element=prefer_element,
                        limit=candidate_limit,
                    )

                with timed_block(
                    f"DiscoveryGraphBuilder.preload_quality material_id={material_id} count={len(candidates)}"
                ):
                    self._preload_material_quality(
                        [
                            candidate["material_id"]
                            for candidate in candidates
                        ]
                    )

                adjacency.setdefault(material_id, [])

                with timed_block(
                    f"DiscoveryGraphBuilder.process_candidates material_id={material_id} count={len(candidates)}"
                ):
                    for candidate in candidates:
                        target_id = candidate["material_id"]

                        with timed_block(
                            f"DiscoveryGraphBuilder.candidate_to_node source={material_id} target={target_id}"
                        ):
                            target_node = self._candidate_to_node(candidate)

                        nodes_by_id[target_id] = target_node

                        with timed_block(
                            f"DiscoveryGraphBuilder.build_transition source={material_id} target={target_id}"
                        ):
                            transition = self._build_transition(
                                from_material=source_node,
                                to_candidate=target_node,
                                elements_map=elements_map,
                                avoid_element=avoid_element,
                                prefer_element=prefer_element,
                            )

                        if transition is None:
                            continue

                        with timed_block(
                            f"DiscoveryGraphBuilder.build_edge source={material_id} target={target_id}"
                        ):
                            edge = self._build_edge(
                                source_material_id=material_id,
                                target_material_id=target_id,
                                transition=transition,
                                candidate=candidate,
                                hop_depth=depth + 1,
                            )

                        edge_key = (
                            edge["source_material_id"],
                            edge["target_material_id"],
                            edge["transition_type"],
                        )

                        edges_by_key[edge_key] = edge

                        if target_id not in adjacency[material_id]:
                            adjacency[material_id].append(target_id)

                        if target_id not in visited:
                            queue.append((target_id, depth + 1))

            with timed_block(
                f"DiscoveryGraphBuilder.response_build start_material_id={start_material_id}"
            ):
                return {
                    "nodes": sorted(
                        nodes_by_id.values(),
                        key=lambda item: (
                            0 if item["material_id"] == start_material_id else 1,
                            item["material_id"],
                        ),
                    ),
                    "edges": sorted(
                        edges_by_key.values(),
                        key=lambda item: (
                            item.get("hop_depth", 999),
                            item["source_material_id"],
                            item["target_material_id"],
                            item["transition_type"],
                        ),
                    ),
                    "adjacency": {
                        source_id: sorted(target_ids)
                        for source_id, target_ids in sorted(adjacency.items())
                    },
                }

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

    def _preload_material_quality(self, material_ids: list[int]) -> None:
        missing_ids = [
            material_id
            for material_id in dict.fromkeys(material_ids)
            if material_id not in self._quality_cache
        ]

        if not missing_ids:
            return

        self._quality_cache.update(
            self.material_quality_service.get_material_quality_bulk(missing_ids)
        )

    def _get_candidates(
        self,
        material_id: int,
        avoid_element: str | None,
        prefer_element: str | None,
        limit: int | None = None,
    ) -> list[dict]:
        result = self.candidate_service.get_discovery_candidates(
            material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            limit=limit or self.EXPANSION_LIMIT,
            include_recommendations=False,
            include_scenarios=False,
            include_substitution_paths=False,
        )

        return [
            candidate
            for candidate in result["candidates"]
            if not (candidate.get("mp_id") or "").startswith("mp-test")
        ]

    def _build_transition(
        self,
        from_material: dict,
        to_candidate: dict,
        elements_map: dict[int, list[str]],
        avoid_element: str | None,
        prefer_element: str | None,
    ) -> dict | None:
        from_elements = elements_map.get(from_material["material_id"], [])
        to_elements = elements_map.get(to_candidate["material_id"], [])

        relationships = self._get_relationships_between(
            from_material_id=from_material["material_id"],
            to_material_id=to_candidate["material_id"],
        )

        return self.transition_validator.validate_transition(
            from_material=from_material,
            to_material=to_candidate,
            from_elements=from_elements,
            to_elements=to_elements,
            relationships=relationships,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
        )

    def _build_edge(
        self,
        source_material_id: int,
        target_material_id: int,
        transition: dict,
        candidate: dict,
        hop_depth: int,
    ) -> dict:
        preserved_framework = transition.get("preserved_framework", [])
        transition_type = transition.get("transition_type")
        removed_elements = transition.get("removed_elements", [])
        introduced_elements = transition.get("introduced_elements", [])

        family = self._infer_family(
            transition_type=transition_type,
            preserved_framework=preserved_framework,
            candidate=candidate,
        )

        scientific_reason = (
            transition.get("scientific_reason")
            or transition.get("reason")
            or "Scientific transition identified by deterministic graph rules."
        )

        edge_intelligence = self.edge_intelligence_service.build_edge_intelligence(
            transition_type=transition_type,
            family=family,
            preserved_framework=preserved_framework,
            removed_elements=removed_elements,
            introduced_elements=introduced_elements,
            scientific_reason=scientific_reason,
        )

        return {
            "source_material_id": source_material_id,
            "target_material_id": target_material_id,
            "transition_type": transition_type,
            "family": family,
            "preserved_framework": preserved_framework,
            "removed_elements": removed_elements,
            "introduced_elements": introduced_elements,
            **edge_intelligence,
            "hop_depth": hop_depth,
        }

    def _infer_family(
        self,
        transition_type: str | None,
        preserved_framework: list[str],
        candidate: dict,
    ) -> str | None:
        framework = set(preserved_framework)
        paths = set(candidate.get("discovery_path", []))

        if "phosphate_related" in paths or {"P", "O"}.issubset(framework):
            return "phosphate"

        if "oxide_related" in paths or "O" in framework:
            return "oxide"

        if transition_type == "alkali_substitution":
            return "alkali"

        return None

    def _get_relationships_between(
        self,
        from_material_id: int,
        to_material_id: int,
    ) -> list[str]:
        cache_key = (from_material_id, to_material_id)

        if cache_key in self._relationship_cache:
            return self._relationship_cache[cache_key]

        family_result = self._get_family_result(from_material_id)

        relationships = []

        for candidate in family_result["related_materials"]:
            if candidate["material_id"] == to_material_id:
                relationships = candidate["relationships"]
                break

        self._relationship_cache[cache_key] = relationships
        return relationships

    def _get_material_elements_map(self) -> dict[int, list[str]]:
        rows = (
            self.db.query(
                MaterialElement.material_id,
                Element.symbol,
            )
            .join(Element, MaterialElement.element_id == Element.id)
            .all()
        )

        elements_map: dict[int, set[str]] = {}

        for material_id, symbol in rows:
            elements_map.setdefault(material_id, set()).add(symbol)

        return {
            material_id: sorted(symbols)
            for material_id, symbols in elements_map.items()
        }

    def _material_to_node(self, material: Material) -> dict:
        quality = self._get_material_quality(material.id)

        return {
            "material_id": material.id,
            "mp_id": material.mp_id,
            "pretty_formula": material.pretty_formula,
            "formula": material.pretty_formula or material.formula,
            **quality,
        }

    def _candidate_to_node(self, candidate: dict) -> dict:
        quality = self._get_material_quality(candidate["material_id"])

        return {
            "material_id": candidate["material_id"],
            "mp_id": candidate["mp_id"],
            "pretty_formula": candidate["pretty_formula"],
            "formula": candidate["pretty_formula"] or candidate["formula"],
            **quality,
        }

    def _get_family_result(self, material_id: int) -> dict:
        if material_id not in self._family_result_cache:
            self._family_result_cache[material_id] = (
                self.family_service.get_material_families(material_id)
            )

        return self._family_result_cache[material_id]

    def _get_material_quality(self, material_id: int) -> dict:
        if material_id not in self._quality_cache:
            self._quality_cache[material_id] = (
                self.material_quality_service.get_material_quality(material_id)
            )

        return self._quality_cache[material_id]