from sqlalchemy.orm import Session

from app.services.research.objective_service import ResearchObjectiveService
from app.utils.chemical_formula import contains_element


class ResearchObjectiveExplorationService:
    def __init__(self, db: Session):
        self.db = db
        self.objective_service = ResearchObjectiveService(db)

    def explore(self, material_id: int, request) -> dict:
        chain_result = self.objective_service.generate_chains_for_objective(
            material_id=material_id,
            objective=request.objective,
        )

        chains = chain_result.get("chains", [])
        candidates = self._rank_candidates_from_chains(
            chains=chains,
            objective=request.objective,
            mode=request.mode,
        )

        return {
            "material_id": material_id,
            "base_formula": chain_result.get("base_formula"),
            "objective": request.objective,
            "mode": request.mode,
            "ranked_candidates": candidates[: request.limit],
            "chains": chains[: request.limit],
            "warnings": self._build_global_warnings(request.mode),
            "explanation": self._build_explanation(request.mode),
        }

    def _rank_candidates_from_chains(self, chains, objective, mode: str) -> list[dict]:
        candidate_map: dict[int, dict] = {}

        for chain in chains:
            materials = chain.get("materials", [])
            transitions = chain.get("transitions", [])

            for material in materials[1:]:
                material_id = material["material_id"]

                if material_id not in candidate_map:
                    candidate_map[material_id] = {
                        "material_id": material_id,
                        "formula": material.get("formula") or material.get("pretty_formula"),
                        "score": 0.0,
                        "reasons": [],
                        "warnings": [],
                    }

                candidate = candidate_map[material_id]
                score = self._score_material(
                    material=material,
                    transitions=transitions,
                    objective=objective,
                    mode=mode,
                )

                candidate["score"] = max(candidate["score"], score)

                candidate["reasons"].extend(
                    self._build_reasons(
                        material=material,
                        transitions=transitions,
                        objective=objective,
                    )
                )

                candidate["warnings"].extend(
                    self._build_candidate_warnings(
                        material=material,
                        objective=objective,
                        mode=mode,
                    )
                )

                candidate["reasons"] = list(dict.fromkeys(candidate["reasons"]))
                candidate["warnings"] = list(dict.fromkeys(candidate["warnings"]))

        return sorted(
            candidate_map.values(),
            key=lambda item: item["score"],
            reverse=True,
        )

    def _score_material(self, material, transitions, objective, mode: str) -> float:
        score = 50.0

        formula = material.get("formula", "")

        for element in objective.prefer_elements:
            if contains_element(formula, element):
                score += 15.0

        for element in objective.avoid_elements:
            if contains_element(formula, element):
                score -= 25.0 if mode != "exploratory" else 10.0

        for transition in transitions:
            preserved = set(transition.get("shared_elements") or transition.get("preserved_framework", []))
            required = set(objective.preserve_elements)

            if required and required.issubset(preserved):
                score += 20.0

            if transition.get("transition_type") == "alkali_substitution":
                score += 10.0

            if transition.get("family") == objective.target_family:
                score += 10.0

        if mode == "exploratory":
            score += 5.0

        return round(score, 2)

    def _build_reasons(self, material, transitions, objective) -> list[str]:
        reasons = []

        formula = material.get("formula", "")

        for element in objective.prefer_elements:
            if contains_element(formula, element):
                reasons.append(f"Candidate contains preferred element {element}.")

        for transition in transitions:
            transition_type = transition.get("transition_type")
            if transition_type:
                reasons.append(f"Connected through {transition_type} pathway.")

            shared_elements = transition.get("shared_elements") or transition.get("preserved_framework", [])
            if shared_elements:
                reasons.append(
                    f"Shares elements across the transition: {', '.join(shared_elements)}. "
                    "Structural preservation is not validated."
                )

        return list(dict.fromkeys(reasons))

    def _build_candidate_warnings(self, material, objective, mode: str) -> list[str]:
        warnings = []

        formula = material.get("formula", "")

        for element in objective.avoid_elements:
            if contains_element(formula, element):
                message = f"Candidate still contains avoided element {element}."
                if mode == "strict":
                    message += " Strict mode should treat this as a hard rejection."
                warnings.append(message)

        return warnings

    def _build_global_warnings(self, mode: str) -> list[str]:
        if mode == "exploratory":
            return [
                "Exploratory mode includes weaker or unusual candidates for broader scientific search."
            ]

        if mode == "strict":
            return [
                "Strict mode is intended for explicit hard constraints and may exclude scientifically interesting candidates."
            ]

        return [
            "Balanced mode ranks, explains, and warns without aggressively discarding candidates."
        ]

    def _build_explanation(self, mode: str) -> str:
        return (
            "Research Objective Exploration combines existing objective chains, "
            "scientific transitions, shared-element continuity, preferred elements, "
            "avoid-element warnings, and exploration mode into a ranked research view. "
            f"Current mode: {mode}."
        )