from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Application, ApplicationStatus, User
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate, DashboardStats

router = APIRouter(tags=["applications"])


def owned_application(db: Session, user_id: UUID, application_id: UUID) -> Application:
    application = db.scalar(select(Application).where(Application.id == application_id, Application.user_id == user_id))
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found")
    return application


@router.post("/applications", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Application:
    data = payload.model_dump()
    if data.get("job_url") is not None:
        data["job_url"] = str(data["job_url"])
    application = Application(user_id=user.id, **data)
    db.add(application)
    db.commit()
    db.refresh(application)
    return application


@router.get("/applications", response_model=list[ApplicationRead])
def list_applications(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> list[Application]:
    return list(db.scalars(select(Application).where(Application.user_id == user.id).order_by(Application.created_at.desc())).all())


@router.get("/applications/{application_id}", response_model=ApplicationRead)
def get_application(application_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Application:
    return owned_application(db, user.id, application_id)


@router.patch("/applications/{application_id}", response_model=ApplicationRead)
def update_application(application_id: UUID, payload: ApplicationUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Application:
    application = owned_application(db, user.id, application_id)
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key in {"company", "position", "status"} and value is None:
            raise HTTPException(status_code=422, detail=f"{key} cannot be null")
        if key == "job_url" and value is not None:
            value = str(value)
        setattr(application, key, value)
    db.commit()
    db.refresh(application)
    return application


@router.delete("/applications/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> Response:
    application = owned_application(db, user.id, application_id)
    db.delete(application)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/dashboard/stats", response_model=DashboardStats)
def dashboard_stats(db: Session = Depends(get_db), user: User = Depends(get_current_user)) -> DashboardStats:
    applications = list(db.scalars(select(Application).where(Application.user_id == user.id)).all())
    total = len(applications)
    interviews = sum(item.status == ApplicationStatus.INTERVIEW for item in applications)
    applied = sum(item.status in {ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEW, ApplicationStatus.OFFER, ApplicationStatus.REJECTED} for item in applications)
    return DashboardStats(
        total=total,
        saved=sum(item.status == ApplicationStatus.SAVED for item in applications),
        applied=applied,
        interviews=interviews,
        offers=sum(item.status == ApplicationStatus.OFFER for item in applications),
        rejected=sum(item.status == ApplicationStatus.REJECTED for item in applications),
        interview_conversion_percent=round((interviews / applied) * 100, 1) if applied else 0.0,
    )
