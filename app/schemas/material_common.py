from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MaterialIdentity(BaseModel):
    material_id: int
    mp_id: str | None = None
    pretty_formula: str | None = None
    formula: str | None = None


class MaterialSummary(MaterialIdentity):
    material_type: str | None = None
    is_stable: bool | None = None
    energy_above_hull: float | None = None


class MaterialRiskSummary(MaterialSummary):
    criticality_score: float | None = None


class MaterialRelationshipSummary(BaseModel):
    shared_element_count: int
    shared_application_count: int
    relationship_types: list[str]