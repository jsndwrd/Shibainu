from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from models import Cluster
from schemas.cluster import ClusterDetailResponse, ClusterResponse
from services.clusterer import ClustererService

router = APIRouter()


@router.get("/", response_model=list[ClusterResponse])
async def get_all_clusters(db: Session = Depends(get_db)):
    return (
        db.query(Cluster)
        .order_by(Cluster.last_updated.desc())
        .all()
    )


@router.get("/{cluster_id}", response_model=ClusterDetailResponse)
async def get_cluster_by_id(cluster_id: UUID, db: Session = Depends(get_db)):
    result = (
        db.query(Cluster)
        .filter(Cluster.id == cluster_id)
        .first()
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    return result


@router.post("/recompute", status_code=status.HTTP_200_OK)
async def recompute_clusters(db: Session = Depends(get_db)):
    service = ClustererService(db)
    service.recompute_clusters()

    return {
        "message": "Cluster recomputation triggered",
    }