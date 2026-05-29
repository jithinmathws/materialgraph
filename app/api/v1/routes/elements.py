from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.element import Element
from app.schemas.element import ElementRead

router = APIRouter(prefix="/elements", tags=["Elements"])


@router.get("", response_model=list[ElementRead])
def list_elements(db: Session = Depends(get_db)):
    return db.query(Element).order_by(Element.symbol).all()


@router.get("/{element_id}", response_model=ElementRead)
def get_element(element_id: int, db: Session = Depends(get_db)):
    element = db.query(Element).filter(Element.id == element_id).first()

    if element is None:
        raise HTTPException(status_code=404, detail="Element not found")

    return element