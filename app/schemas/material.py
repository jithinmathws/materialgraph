from pydantic import BaseModel, ConfigDict


class MaterialRead(BaseModel):
    id: int
    mp_id: str
    formula: str
    pretty_formula: str
    material_type: str | None = None
    band_gap: float | None = None
    energy_above_hull: float | None = None
    formation_energy_per_atom: float | None = None
    density: float | None = None
    is_stable: bool
    source: str

    model_config = ConfigDict(from_attributes=True)

class ElementSummary(BaseModel):
    id: int
    symbol: str
    name: str

    model_config = ConfigDict(from_attributes=True)


class MaterialDetail(MaterialRead):
    elements: list[ElementSummary]