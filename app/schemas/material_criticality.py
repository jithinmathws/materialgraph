from pydantic import BaseModel, ConfigDict


class MaterialCriticalityElement(BaseModel):
    element_id: int
    symbol: str
    name: str

    fraction: float
    risk_year: int | None

    abundance_score: float | None
    supply_risk_score: float | None
    toxicity_score: float | None
    recyclability_score: float | None
    geopolitical_risk_score: float | None

    criticality_known: bool
    element_criticality_score: float | None


class MaterialCriticalityResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    material_id: int
    mp_id: str | None
    pretty_formula: str | None
    formula: str | None

    criticality_score: float | None
    criticality_known: bool

    criticality_profile_coverage: float
    criticality_fraction_coverage: float

    known_criticality_element_count: int
    unknown_criticality_element_count: int
    total_element_count: int

    known_criticality_fraction: float
    unknown_criticality_fraction: float

    criticality_evidence_complete: bool
    unknown_criticality_elements: list[str]

    elements: list[MaterialCriticalityElement]