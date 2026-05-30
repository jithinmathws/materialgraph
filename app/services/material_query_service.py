from sqlalchemy.orm import Session

from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement


class MaterialQueryService:
    def __init__(self, db: Session):
        self.db = db

    def get_material_with_elements(
        self,
        material_id: int,
    ) -> tuple[Material, list[Element]] | None:
        material = (
            self.db.query(Material)
            .filter(Material.id == material_id)
            .first()
        )

        if material is None:
            return None

        elements = (
            self.db.query(Element)
            .join(MaterialElement, Element.id == MaterialElement.element_id)
            .filter(MaterialElement.material_id == material_id)
            .order_by(Element.symbol)
            .all()
        )

        return material, elements