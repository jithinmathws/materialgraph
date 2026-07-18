from sqlalchemy.orm import Session

from app.services.discovery.chain_service import DiscoveryChainService
from app.services.discovery.path_ranking_service import DiscoveryPathRankingService


class ResearchObjectiveService:
    def __init__(self, db: Session):
        self.db = db
        self.chain_service = DiscoveryChainService(db)
        self.path_ranking_service = DiscoveryPathRankingService(db)

    def generate_chains_for_objective(
        self,
        material_id: int,
        objective,
    ) -> dict:
        result = self.chain_service.get_discovery_chains(
            material_id=material_id,
            avoid_elements=objective.avoid_elements,
            prefer_elements=objective.prefer_elements,
            max_hops=objective.max_hops,
            limit=objective.limit,
        )

        filtered_chains = self._filter_chains(
            chains=result["chains"],
            objective=objective,
        )

        ranked_chains = self._rank_chains(
            chains=filtered_chains,
            objective=objective,
        )

        return {
            "material_id": result["material_id"],
            "base_formula": result["base_formula"],
            "objective": objective,
            "chains": ranked_chains,
        }

    def _filter_chains(
        self,
        chains: list[dict],
        objective,
    ) -> list[dict]:
        filtered = []

        for chain in chains:
            if not self._preserves_required_elements(
                chain,
                objective.preserve_elements,
            ):
                continue

            if not self._matches_target_family(
                chain,
                objective.target_family,
            ):
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
            all_preserved.update(
                transition.get("shared_elements")
                or transition.get("preserved_framework", [])
            )

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
                shared_elements = (
                    transition.get("shared_elements")
                    or transition.get("preserved_framework", [])
                )
                if required.issubset(set(shared_elements)):
                    return True

        for transition in chain["transitions"]:
            transition_type = transition.get("transition_type", "")
            reason = (
                transition.get("scientific_reason")
                or transition.get("reason")
                or ""
            )

            if target in transition_type.lower():
                return True

            if target in reason.lower():
                return True

        return False

    def _rank_chains(
        self,
        chains: list[dict],
        objective,
    ) -> list[dict]:
        ranked_chains = []

        for chain in chains:
            ranking = self.path_ranking_service.rank_path(
                materials=chain["materials"],
                transitions=chain["transitions"],
                avoid_elements=objective.avoid_elements,
                prefer_elements=objective.prefer_elements,
            )

            ranked_chains.append({
                **chain,
                **ranking,
            })

        ranked_chains.sort(
            key=lambda item: item["scientific_usefulness_score"],
            reverse=True,
        )

        return ranked_chains
