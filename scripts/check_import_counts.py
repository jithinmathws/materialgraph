# scripts/check_import_counts.py

from sqlalchemy import func

from app.core.database import SessionLocal
from app.models.element import Element
from app.models.material import Material
from app.models.material_element import MaterialElement


def main():
    db = SessionLocal()

    try:
        materials = db.query(func.count(Material.id)).scalar()
        elements = db.query(func.count(Element.id)).scalar()
        material_elements = db.query(func.count(MaterialElement.id)).scalar()

        print(f"Materials: {materials}")
        print(f"Elements: {elements}")
        print(f"MaterialElements: {material_elements}")

    finally:
        db.close()


if __name__ == "__main__":
    main()