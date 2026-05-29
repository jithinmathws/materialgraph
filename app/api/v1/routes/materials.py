from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.material import Material
from app.schemas.material import MaterialRead

router = APIRouter(prefix="/materials", tags=["Materials"])


@router.get("", response_model=list[MaterialRead])
def list_materials(db: Session = Depends(get_db)):
    return db.query(Material).order_by(Material.id).all()


@router.get("/{material_id}", response_model=MaterialRead)
def get_material(material_id: int, db: Session = Depends(get_db)):
    material = db.query(Material).filter(Material.id == material_id).first()

    if material is None:
        raise HTTPException(status_code=404, detail="Material not found")

    return material