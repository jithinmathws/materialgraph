from pydantic import BaseModel, ConfigDict


class ElementRead(BaseModel):
    id: int
    symbol: str
    name: str
    atomic_number: int | None = None
    category: str | None = None

    model_config = ConfigDict(from_attributes=True)