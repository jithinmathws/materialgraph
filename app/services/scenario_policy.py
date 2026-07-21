from dataclasses import dataclass, field

from app.utils.chemical_formula import contains_element


@dataclass(frozen=True)
class ScenarioPolicy:
    element: str
    supply_risk_multiplier: float = 1.0
    avoid_elements: list[str] = field(default_factory=list)
    prefer_elements: list[str] = field(default_factory=list)
    penalties: dict[str, float] = field(default_factory=dict)
    bonuses: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class ScenarioPolicyResult:
    scenario_score: float
    scenario_delta: float
    scenario_reason: str


class ScenarioPolicyEvaluator:
    DEFAULT_AVOID_ELEMENT_PENALTY = 20.0
    DEFAULT_PREFER_ELEMENT_BONUS = 10.0

    def evaluate(
        self,
        recommendation_score: float,
        candidate_formula: str,
        policy: ScenarioPolicy,
    ) -> ScenarioPolicyResult:
        score = recommendation_score
        reasons: list[str] = []

        if policy.supply_risk_multiplier != 1.0:
            score *= policy.supply_risk_multiplier
            reasons.append(
                f"supply risk multiplier {policy.supply_risk_multiplier} applied"
            )

        avoided = [
            avoid_element
            for avoid_element in policy.avoid_elements
            if contains_element(candidate_formula, avoid_element)
        ]

        if avoided:
            penalty = self.DEFAULT_AVOID_ELEMENT_PENALTY * len(avoided)
            score -= penalty
            reasons.append(
                f"contains avoided element {', '.join(avoided)}, penalty {penalty}"
            )

        preferred = [
            prefer_element
            for prefer_element in policy.prefer_elements
            if contains_element(candidate_formula, prefer_element)
        ]

        if preferred:
            bonus = self.DEFAULT_PREFER_ELEMENT_BONUS * len(preferred)
            score += bonus
            reasons.append(
                f"contains preferred element {', '.join(preferred)}, bonus {bonus}"
            )

        scenario_score = round(score, 2)
        scenario_delta = round(scenario_score - recommendation_score, 2)

        if scenario_delta > 0:
            reasons.append(f"final scenario bonus {scenario_delta}")
        elif scenario_delta < 0:
            reasons.append(f"final scenario penalty {abs(scenario_delta)}")
        else:
            reasons.append("no final scenario adjustment")

        return ScenarioPolicyResult(
            scenario_score=scenario_score,
            scenario_delta=scenario_delta,
            scenario_reason="; ".join(reasons),
        )