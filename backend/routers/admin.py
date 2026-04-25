from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.database import get_db
from services.demo import DemoSeedService

router = APIRouter()

@router.post('/seed-demo')
async def seedDemoData(
    count: int = Query(default=120, ge=80, le=300),
    db: Session = Depends(get_db),
):
    service = DemoSeedService(db)
    return service.seedDemoData(total_aspirations=count)

@router.get("/stats")
async def getStats(db: Session = Depends(get_db)):
    service = DemoSeedService(db)
    return service.getStats()


@router.post('/reindex')
async def reindex():
    return {
        "message": "Reindex endpoint is ready. Connect this to cluster and score recomputation service.",
    }