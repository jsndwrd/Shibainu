from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from schemas.brief import BriefGenerateRequest, BriefResponse
from services.brief_generator import BriefGeneratorService

router = APIRouter()


@router.post("/generate", response_model=list[BriefResponse], status_code=status.HTTP_201_CREATED)
async def generate_brief(payload: BriefGenerateRequest, db: Session = Depends(get_db)):
    service = BriefGeneratorService(db)
    return service.generateMany(payload.cluster_ids)


@router.get("/", response_model=list[BriefResponse])
async def get_all_briefs(db: Session = Depends(get_db)):
    service = BriefGeneratorService(db)
    return service.getAllBriefs()


@router.get("/{brief_id}", response_model=BriefResponse)
async def get_brief_by_id(brief_id: UUID, db: Session = Depends(get_db)):
    service = BriefGeneratorService(db)
    result = service.getBrief(brief_id)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brief not found",
        )

    return result