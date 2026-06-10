from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.application import Application
from app.schemas.application import ApplicationRead

router = APIRouter(prefix="/applications", tags=["Applications"])


@router.get(
    "",
    response_model=list[ApplicationRead],
    summary="List applications",
    description="Returns material application categories ordered by name.",
)
def list_applications(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return (
        db.query(Application)
        .order_by(Application.name)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).filter(Application.id == application_id).first()

    if application is None:
        raise HTTPException(status_code=404, detail="Application not found")

    return application