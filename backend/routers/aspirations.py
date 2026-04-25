from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user

from schemas.aspiration import (
    AspirationCreate,
    AspirationResponse,
    AspirationListItem,
)

from services.aspiration_service import AspirationService

router = APIRouter()

@router.post('/', response_model=AspirationResponse, status_code=status.HTTP_201_CREATED)
async def postAspiration(payload: AspirationCreate, currUser=Depends(get_current_user), db: Session = Depends(get_db)):
    serv = AspirationService(db)
    res = serv.createAspiration(citizen_id=currUser, payload=payload)
    return res


@router.get('/', response_model=list[AspirationListItem])
async def getAllAspirations(db: Session = Depends(get_db)):
    serv = AspirationService(db)
    return serv.getAllAspirations()

@router.get("/{aspiration_id}")
async def getAspirationById(aspiration_id: UUID, db: Session = Depends(get_db)):
    serv = AspirationService(db)
    res = serv.getAspirationById(aspiration_id)
    
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aspiration Not Found"
        )
    
    return res

@router.get("/{citizen_id}")
async def getAspirationsByCitizenId(citizen_id: UUID, db: Session = Depends(get_db)):
    serv = AspirationService(db)
    return serv.getMyAspiration(citizen_id=citizen_id)

@router.get("/mine", response_model=list[AspirationListItem])
async def getMyAspirations(currUser=Depends(get_current_user), db: Session = Depends(get_db)):
    serv = AspirationService(db)
    return serv.getMyAspiration(citizen_id=currUser)

@router.patch('/{aspiration_id}/status', response_model=AspirationResponse)
async def updateAspirationStatus(aspiration_id: UUID, status: str, db: Session = Depends(get_db)):
    serv = AspirationService(db)
    res = serv.updateStatus(aspiration_id=aspiration_id, status=status)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Aspiration Not Found'
        )
    
    return res