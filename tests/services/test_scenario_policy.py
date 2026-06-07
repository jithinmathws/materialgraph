from app.services.scenario_policy import ScenarioPolicy, ScenarioPolicyEvaluator


def test_policy_penalizes_avoided_element():
    evaluator = ScenarioPolicyEvaluator()

    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="LiCoO2",
        policy=ScenarioPolicy(
            element="Li",
            avoid_elements=["Co"],
        ),
    )

    assert result.scenario_score == 80.0
    assert result.scenario_delta == -20.0
    assert "contains avoided element Co" in result.scenario_reason


def test_policy_rewards_preferred_element():
    evaluator = ScenarioPolicyEvaluator()

    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="NaFeO2",
        policy=ScenarioPolicy(
            element="Li",
            prefer_elements=["Na"],
        ),
    )

    assert result.scenario_score == 110.0
    assert result.scenario_delta == 10.0
    assert "contains preferred element Na" in result.scenario_reason


def test_policy_combines_multiplier_penalty_and_bonus():
    evaluator = ScenarioPolicyEvaluator()

    result = evaluator.evaluate(
        recommendation_score=100.0,
        candidate_formula="NaCoO2",
        policy=ScenarioPolicy(
            element="Li",
            supply_risk_multiplier=1.5,
            avoid_elements=["Co"],
            prefer_elements=["Na"],
        ),
    )

    assert result.scenario_score == 140.0
    assert result.scenario_delta == 40.0
    assert "supply risk multiplier 1.5 applied" in result.scenario_reason
    assert "contains avoided element Co" in result.scenario_reason
    assert "contains preferred element Na" in result.scenario_reason