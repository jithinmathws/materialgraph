from sqlalchemy.orm import Session

from app.services.discovery_chain_service import DiscoveryChainService


class ResearchObjectiveService:
    def __init__(self, db: Session):
        self.db = db
        self.chain_service = DiscoveryChainService(db)

    def generate_chains_for_objective(
        self,
        material_id: int,
        objective,
    ) -> dict:
        avoid_element = (
            objective.avoid_elements[0]
            if objective.avoid_elements
            else None
        )

        prefer_element = (
            objective.prefer_elements[0]
            if objective.prefer_elements
            else None
        )

        result = self.chain_service.get_discovery_chains(
            material_id=material_id,
            avoid_element=avoid_element,
            prefer_element=prefer_element,
            max_hops=objective.max_hops,
            limit=objective.limit,
        )

        filtered_chains = self._filter_chains(
            chains=result["chains"],
            objective=objective,
        )

        return {
            "material_id": result["material_id"],
            "base_formula": result["base_formula"],
            "objective": objective,
            "chains": filtered_chains,
        }

    def _filter_chains(
        self,
        chains: list[dict],
        objective,
    ) -> list[dict]:
        filtered = []

        for chain in chains:
            if not self._preserves_required_elements(chain, objective.preserve_elements):
                continue

            if not self._matches_target_family(chain, objective.target_family):
                continue

            filtered.append(chain)

        return filtered

    def _preserves_required_elements(
        self,
        chain: dict,
        preserve_elements: list[str],
    ) -> bool:
        if not preserve_elements:
            return True

        required = set(preserve_elements)

        all_preserved = set()

        for transition in chain["transitions"]:
            all_preserved.update(transition["preserved_framework"])

        return required.issubset(all_preserved)

    def _matches_target_family(
        self,
        chain: dict,
        target_family: str | None,
    ) -> bool:
        if target_family is None:
            return True

        target = target_family.lower()

        if target == "phosphate":
            required = {"P", "O"}

            for transition in chain["transitions"]:
                if required.issubset(set(transition["preserved_framework"])):
                    return True

        for transition in chain["transitions"]:
            if target in transition["transition_type"].lower():
                return True

            reason = (
                transition.get("scientific_reason")
                or transition.get("reason")
                or ""
            )

            if target in transition["reason"].lower():
                return True

        return False