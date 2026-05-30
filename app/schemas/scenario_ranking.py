from pydantic import BaseModel


class ScenarioRankingRequest(BaseModel):
    scenario_name: str
    top_n: int = 10


class ScenarioRankingResult(BaseModel):
    rank: int
    scenario_name: str
    material_id: int
    mp_id: str
    formula: str
    pretty_formula: str
    score: float
    material_risk_score: float
    risk_penalty: float
    reasons: list[str]
    ranking_explanation: list[str]