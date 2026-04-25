from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.brief import (BriefGenerateRequest, BriefResponse)
from services.brief_generator import BriefGeneratorService

router = APIRouter()

@router.post('/generate', response_model=list[BriefResponse], status_code=status.HTTP_201_CREATED)
async def generateBrief(payload: BriefGenerateRequest, db: Session = Depends(get_db)):
    serv = BriefGeneratorService(db)
    res = serv.generateMany(payload.cluster_ids)

    return res


@router.get('/', response_model=list[BriefResponse])
async def getAllBriefs(db: Session = Depends(get_db)):
    serv = BriefGeneratorService(db)

    return (db.query(serv.db.registry.mapped["PolicyBrief"]).order_by(serv.db.registry.mapped["PolicyBrief"].generated_at.desc()).all())

@router.get('/{brief_id}', response_model=BriefResponse)
async def getBriefById(brief_id: UUID, db: Session = Depends(get_db)):
    serv = BriefGeneratorService(db)
    res = serv.getBrief(brief_id)

    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brief Not Found"
        )
    
    return res