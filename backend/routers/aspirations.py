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

@router.get('/', response_model=list[AspirationListItem])
async def getAllAspirations(db: Session = Depends(get_db)):
    serv = AspirationService(db)
    return serv.getAllAspirations()

@router.get("/mine", response_model=list[AspirationListItem])
async def getMyAspirations(
    currUser=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    serv = AspirationService(db)
    return serv.getMyAspiration(citizen_id=currUser)


@router.get("/citizen/{citizen_id}", response_model=list[AspirationListItem])
async def getAspirationsByCitizenId(
    citizen_id: UUID,
    db: Session = Depends(get_db)
):
    serv = AspirationService(db)
    return serv.getMyAspiration(citizen_id=citizen_id)


@router.get("/{aspiration_id}")
async def getAspirationById(
    aspiration_id: UUID,
    db: Session = Depends(get_db)
):
    serv = AspirationService(db)
    res = serv.getAspirationById(aspiration_id)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aspiration Not Found"
        )

    return res

@router.patch('/{aspiration_id}/status', response_model=AspirationResponse)
async def updateAspirationStatus(aspiration_id: UUID, status: str, db: Session = Depends(get_db)):
    serv = AspirationService(db)
    res = serv.updateStatus(aspiration_id=aspiration_id, status=status)

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