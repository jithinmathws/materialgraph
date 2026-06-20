from collections import deque

from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement
from app.services.discovery_candidate_service import DiscoveryCandidateService
from app.services.discovery_transition_validator import DiscoveryTransitionValidator
from app.services.material_family_service import MaterialFamilyService


class DiscoveryChainService:
    DEFAULT_MAX_HOPS = 2
    MAX_ALLOWED_HOPS = 3
    DEFAULT_LIMIT = 5
    EXPANSION_LIMIT = 20

    def __init__(self, db: Session):
        self.db = db
        self.candidate_service = DiscoveryCandidateService(db)
        self.family_service = MaterialFamilyService(db)
        self.transition_validator = DiscoveryTransitionValidator()

    def get_discovery_chains(
        self,
        material_id: int,
        avoid_element: str | None = None,
        prefer_element: str | None = None,
        max_hops: int = DEFAULT_MAX_HOPS,
        limit: int = DEFAULT_LIMIT,
    ) -> dict:
        max_hops = min(max_hops, self.MAX_ALLOWED_HOPS)

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
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_hops=max_hops,
            limit=limit,
        )

        return {
            "material_id": base_material.id,
            "mp_id": base_material.mp_id,
            "base_formula": base_material.pretty_formula or base_material.formula,
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
        avoid_element: str | None,
        prefer_element: str | None,
        max_hops: int,
        limit: int,
    ) -> list[dict]:
        queue = deque()

        base_node = self._material_to_node(base_material)

        queue.append(
            {
                "materials": [base_node],
                "transitions": [],
                "visited_ids": {base_material.id},
            }
        )

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

            next_candidates = self._get_next_candidates(
                material_id=current_material["material_id"],
                avoid_element=avoid_element,
                prefer_element=prefer_element,
            )

            for candidate in next_candidates:
                candidate_id = candidate["material_id"]

                if candidate_id in current_chain["visited_ids"]:
                    continue

                transition = self._build_transition(
                    from_material=current_material,
                    to_candidate=candidate,
                    elements_map=elements_map,
                    avoid_element=avoid_element,
                    prefer_element=prefer_element,
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
            to_material=self._candidate_to_node(to_candidate),
            from_elements=from_elements,
            to_elements=to_elements,
            relationships=relationships,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
        )

    def _get_relationships_between(
        self,
        from_material_id: int,
        to_material_id: int,
    ) -> list[str]:
        family_result = self.family_service.get_material_families(from_material_id)

        for candidate in family_result["related_materials"]:
            if candidate["material_id"] == to_material_id:
                return candidate["relationships"]

        return []

    def _finalize_chain(self, chain: dict) -> dict:
        return {
            "hop_count": len(chain["transitions"]),
            "materials": chain["materials"],
            "transitions": chain["transitions"],
            "chain_reason": self._build_chain_reason(chain["transitions"]),
        }

    def _build_chain_reason(self, transitions: list[dict]) -> str:
        if not transitions:
            return "No discovery transition was generated."

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

        reason = (
            "This discovery chain follows "
            + " → ".join(transition_types)
        )

        if common_framework:
            reason += (
                f" while preserving {'-'.join(common_framework)} chemistry"
            )

        return reason + "."

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
        return {
            "material_id": material.id,
            "mp_id": material.mp_id,
            "pretty_formula": material.pretty_formula,
            "formula": material.pretty_formula or material.formula,
        }

    def _candidate_to_node(self, candidate: dict) -> dict:
        return {
            "material_id": candidate["material_id"],
            "mp_id": candidate["mp_id"],
            "pretty_formula": candidate["pretty_formula"],
            "formula": candidate["pretty_formula"] or candidate["formula"],
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