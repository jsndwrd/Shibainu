from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db

from schemas.cluster import (
    ClusterResponse,
    ClusterDetailResponse,
)

from services.clusterer import ClustererService
from models import Cluster

router = APIRouter()

@router.get('/', response_model=list[ClusterResponse])
async def getAllClusters(db: Session = Depends(get_db)):
    return (db.query(Cluster).order_by(Cluster.last_updated.desc()).all())

@router.get('/{cluster_id}', response_model=ClusterDetailResponse)
async def getClusterById(cluster_id: UUID, db: Session = Depends(get_db)):
    res = (db.query(Cluster).filter(Cluster.id == cluster_id).first())
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster Not Found"
        )
    
    return res

@router.post('/recompute', status_code=status.HTTP_200_OK)
async def recomputeClusters(db: Session = Depends(get_db)):
    serv = ClustererService(db)
    serv.recomputeClusters()

    return {"message": "Cluster Recomputation Triggered"}