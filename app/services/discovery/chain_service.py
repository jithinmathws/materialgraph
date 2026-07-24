import time
from collections import deque
from collections.abc import Collection

from loguru import logger
from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.discovery.candidate_service import DiscoveryCandidateService
from app.services.discovery.transition_validator import DiscoveryTransitionValidator
from app.services.material.family_service import MaterialFamilyService
from app.utils.chemical_formula import extract_elements


class DiscoveryChainService:
    DEFAULT_MAX_HOPS = 2
    MAX_ALLOWED_HOPS = 3
    DEFAULT_LIMIT = 5
    EXPANSION_LIMIT = 6

    def __init__(self, db: Session):
        self.db = db
        self.candidate_service = DiscoveryCandidateService(db)
        self.family_service = MaterialFamilyService(db)
        self.transition_validator = DiscoveryTransitionValidator()
        self._candidate_cache: dict[
            tuple[int, tuple[str, ...], tuple[str, ...]],
            list[dict],
        ] = {}
        self._relationship_cache: dict[tuple[int, int], list[str]] = {}
        self._family_result_cache: dict[int, dict] = {}

    def get_discovery_chains(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
        limit: int = DEFAULT_LIMIT,
        avoid_elements: Collection[str] | None = None,
        prefer_elements: Collection[str] | None = None,
    ) -> dict:
        max_hops = min(max_hops, self.MAX_ALLOWED_HOPS)

        normalized_avoid_elements = self._normalize_elements(
            element=avoid_element,
            elements=avoid_elements,
        )
        normalized_prefer_elements = self._normalize_elements(
            element=prefer_element,
            elements=prefer_elements,
        )

        base_material = self.db.get(Material, material_id)

        if base_material is None:
            return self._empty_response(
                material_id=material_id,
                avoid_element=avoid_element,
                prefer_element=prefer_element,
                max_hops=max_hops,
                limit=limit,
            )

        elements_map = self._get_material_elements_map()
        chains = self._build_chains(
            base_material=base_material,
            elements_map=elements_map,
            avoid_elements=normalized_avoid_elements,
            prefer_elements=normalized_prefer_elements,
            max_hops=max_hops,
            limit=limit,
        )

        return {
            "material_id": base_material.id,
            "mp_id": base_material.mp_id,
            "base_formula": (
                base_material.pretty_formula
                or base_material.formula
            ),
            "discovery_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
                "max_hops": max_hops,
                "limit": limit,
            },
            "chains": chains,
        }

    def _build_chains(
        self,
        base_material: Material,
        elements_map: dict[int, list[str]],
        avoid_elements: frozenset[str],
        prefer_elements: frozenset[str],
        max_hops: int,
        limit: int,
    ) -> list[dict]:
        queue = deque()

        base_node = self._material_to_node(base_material)

        queue.append({
            "materials": [base_node],
            "transitions": [],
            "visited_ids": {base_material.id},
        })

        completed_chains = []

        while queue and len(completed_chains) < limit:
            current_chain = queue.popleft()
            current_material = current_chain["materials"][-1]
            current_hops = len(current_chain["transitions"])

            if current_hops >= max_hops:
                completed_chains.append(
                    self._finalize_chain(current_chain)
                )
                continue

            candidate_start = time.perf_counter()
            next_candidates = self._get_next_candidates(
                material_id=current_material["material_id"],
                avoid_elements=avoid_elements,
                prefer_elements=prefer_elements,
                elements_map=elements_map,
            )
            logger.info(
                "Next candidates for material {} took {:.3f}s count={}",
                current_material["material_id"],
                time.perf_counter() - candidate_start,
                len(next_candidates),
            )

            for candidate in next_candidates:
                candidate_id = candidate["material_id"]

                if candidate_id in current_chain["visited_ids"]:
                    continue

                transition_start = time.perf_counter()
                transition = self._build_transition(
                    from_material=current_material,
                    to_candidate=candidate,
                    elements_map=elements_map,
                    avoid_elements=avoid_elements,
                    prefer_elements=prefer_elements,
                )
                logger.info(
                    "Transition {} -> {} took {:.3f}s",
                    current_material["material_id"],
                    candidate_id,
                    time.perf_counter() - transition_start,
                )

                if transition is None:
                    continue

                next_chain = {
                    "materials": [
                        *current_chain["materials"],
                        self._candidate_to_node(candidate),
                    ],
                    "transitions": [
                        *current_chain["transitions"],
                        transition,
                    ],
                    "visited_ids": {
                        *current_chain["visited_ids"],
                        candidate_id,
                    },
                }

                if len(next_chain["transitions"]) == max_hops:
                    completed_chains.append(
                        self._finalize_chain(next_chain)
                    )

                    if len(completed_chains) >= limit:
                        break
                else:
                    queue.append(next_chain)

        return completed_chains[:limit]

    def _get_next_candidates(
        self,
        material_id: int,
        elements_map: dict[int, list[str]],
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        avoid_elements: Collection[str] | None = None,
        prefer_elements: Collection[str] | None = None,
    ) -> list[dict]:
        normalized_avoid_elements = self._normalize_elements(
            element=avoid_element,
            elements=avoid_elements,
        )
        normalized_prefer_elements = self._normalize_elements(
            element=prefer_element,
            elements=prefer_elements,
        )

        cache_key = (
            material_id,
            tuple(sorted(normalized_avoid_elements)),
            tuple(sorted(normalized_prefer_elements)),
        )

        if cache_key in self._candidate_cache:
            return self._candidate_cache[cache_key]

        family_result = self._get_family_result(material_id)
        candidates = []

        for candidate in family_result["related_materials"]:
            mp_id = candidate.get("mp_id") or ""

            if mp_id.startswith("mp-test"):
                continue

            formula = (
                candidate.get("pretty_formula")
                or candidate.get("formula")
                or ""
            )
            candidate_id = candidate["material_id"]

            if candidate_id in elements_map:
                candidate_elements: set[str] | None = set(
                    elements_map[candidate_id]
                )
            else:
                parsed_elements = extract_elements(formula)
                candidate_elements = parsed_elements or None

            if normalized_prefer_elements and (
                candidate_elements is None
                or not candidate_elements.intersection(
                    normalized_prefer_elements
                )
            ):
                continue

            candidates.append(candidate)

            if len(candidates) >= self.EXPANSION_LIMIT:
                break

        self._candidate_cache[cache_key] = candidates
        return candidates

    def _build_transition(
        self,
        from_material: dict,
        to_candidate: dict,
        elements_map: dict[int, list[str]],
        avoid_elements: frozenset[str],
        prefer_elements: frozenset[str],
    ) -> dict | None:
        from_elements = elements_map.get(
            from_material["material_id"],
            [],
        )
        to_elements = elements_map.get(
            to_candidate["material_id"],
            [],
        )

        relationships = self._get_relationships_between(
            from_material_id=from_material["material_id"],
            to_material_id=to_candidate["material_id"],
        )

        return self.transition_validator.validate_transition(
            from_material=from_material,
            to_material=self._candidate_to_node(to_candidate),
            from_elements=from_elements,
            to_elements=to_elements,
            relationships=relationships,
            avoid_elements=avoid_elements,
            prefer_elements=prefer_elements,
        )

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

    def _finalize_chain(self, chain: dict) -> dict:
        return {
            "hop_count": len(chain["transitions"]),
            "materials": chain["materials"],
            "transitions": chain["transitions"],
            "chain_reason": self._build_chain_reason(
                chain["transitions"]
            ),
        }

    def _build_chain_reason(
        self,
        transitions: list[dict],
    ) -> str:
        if not transitions:
            return "No discovery transition was generated."

        transition_types = [
            transition["transition_type"]
            for transition in transitions
        ]

        shared_element_sets = [
            set(
                transition.get("shared_elements")
                or transition.get("preserved_framework", [])
            )
            for transition in transitions
            if (
                transition.get("shared_elements")
                or transition.get("preserved_framework")
            )
        ]

        common_shared_elements = sorted(
            set.intersection(*shared_element_sets)
            if shared_element_sets
            else set()
        )

        reason = (
            "This discovery chain follows "
            + " -> ".join(transition_types)
        )

        if common_shared_elements:
            reason += (
                f" with {'-'.join(common_shared_elements)} "
                "shared-element continuity"
            )

        return reason + "."

    def _get_material_elements_map(
        self,
    ) -> dict[int, list[str]]:
        rows = (
            self.db.query(
                MaterialElement.material_id,
                Element.symbol,
            )
            .join(
                Element,
                MaterialElement.element_id == Element.id,
            )
            .all()
        )

        elements_map: dict[int, set[str]] = {}

        for material_id, symbol in rows:
            elements_map.setdefault(material_id, set()).add(symbol)

        return {
            material_id: sorted(symbols)
            for material_id, symbols in elements_map.items()
        }

    def _material_to_node(
        self,
        material: Material,
    ) -> dict:
        return {
            "material_id": material.id,
            "mp_id": material.mp_id,
            "pretty_formula": material.pretty_formula,
            "formula": material.pretty_formula or material.formula,
        }

    def _candidate_to_node(
        self,
        candidate: dict,
    ) -> dict:
        return {
            "material_id": candidate["material_id"],
            "mp_id": candidate["mp_id"],
            "pretty_formula": candidate["pretty_formula"],
            "formula": (
                candidate["pretty_formula"]
                or candidate["formula"]
            ),
        }

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
            "discovery_goal": {
                "avoid_element": avoid_element,
                "prefer_element": prefer_element,
                "max_hops": max_hops,
                "limit": limit,
            },
            "chains": [],
        }

    def _get_family_result(
        self,
        material_id: int,
    ) -> dict:
        if material_id not in self._family_result_cache:
            self._family_result_cache[material_id] = (
                self.family_service.get_material_families(
                    material_id
                )
            )

        return self._family_result_cache[material_id]

    def _normalize_elements(
        self,
        *,
        element: str | None,
        elements: Collection[str] | None,
    ) -> frozenset[str]:
        normalized = {
            item
            for item in (elements or [])
            if item
        }

        if element:
            normalized.add(element)

        return frozenset(normalized)
