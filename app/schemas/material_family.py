from pydantic import BaseModel


class RelatedMaterialFamily(BaseModel):
    material_id: int
    mp_id: str
    pretty_formula: str
    formula: str
    relationships: list[str]
    shared_elements: list[str]
    relationship_reason: str


class MaterialFamiliesResponse(BaseModel):
    material_id: int
    mp_id: str | None = None
    pretty_formula: str | None = None
    formula: str | None = None
    related_materials: list[RelatedMaterialFamily]