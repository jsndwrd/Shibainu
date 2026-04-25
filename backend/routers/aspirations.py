from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user
from schemas.aspiration import (
    AspirationCreate,
    AspirationListItem,
    AspirationResponse,
)
from services.aspiration_service import AspirationService

router = APIRouter()


@router.post("/", response_model=AspirationResponse, status_code=status.HTTP_201_CREATED)
async def post_aspiration(
    payload: AspirationCreate,
    currUser=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AspirationService(db)
    return service.createAspiration(citizen_id=currUser, payload=payload)


@router.get("/mine", response_model=list[AspirationListItem])
async def get_my_aspirations(
    currUser=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = AspirationService(db)
    return service.getMyAspiration(citizen_id=currUser)


@router.get("/", response_model=list[AspirationListItem])
async def get_all_aspirations(db: Session = Depends(get_db)):
    service = AspirationService(db)
    return service.getAllAspirations()


@router.get("/{aspiration_id}", response_model=AspirationResponse)
async def get_aspiration_by_id(
    aspiration_id: UUID,
    db: Session = Depends(get_db),
):
    service = AspirationService(db)
    result = service.getAspirationById(aspiration_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aspiration not found",
        )

    return result


@router.patch("/{aspiration_id}/status", response_model=AspirationResponse)
async def update_aspiration_status(
    aspiration_id: UUID,
    status_value: str,
    db: Session = Depends(get_db),
):
    service = AspirationService(db)
    result = service.updateStatus(
        aspiration_id=aspiration_id,
        status=status_value,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aspiration not found",
        )

    return result