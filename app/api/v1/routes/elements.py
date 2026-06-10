from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.element import Element
from app.schemas.element import ElementRead

router = APIRouter(prefix="/elements", tags=["Elements"])


@router.get(
    "",
    response_model=list[ElementRead],
    summary="List elements",
    description="Returns elements ordered alphabetically by symbol.",
)
def list_elements(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(Element)
        .order_by(Element.symbol)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{element_id}", response_model=ElementRead)
def get_element(element_id: int, db: Session = Depends(get_db)):
    element = db.query(Element).filter(Element.id == element_id).first()

    if element is None:
        raise HTTPException(status_code=404, detail="Element not found")

    return element