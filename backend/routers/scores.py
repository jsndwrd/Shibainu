from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.database import get_db

from schemas.score import ScoreResponse

from services.scorer import ScorerService
from models import ClusterScore, Cluster

router = APIRouter()

@router.get('/', response_model=list[ScoreResponse])
async def getAllScores(db: Session = Depends(get_db)):
    return (db.query(ClusterScore).order_by(ClusterScore.computed_at.desc()).all())

@router.get('/top', response_model=list[ScoreResponse])
async def getTopScores(db: Session = Depends(get_db)):
    return (db.query(ClusterScore).order_by(ClusterScore.total_score.desc()).limit(10).all())

@router.get('/regional/{province}', response_model=list[ScoreResponse])
async def getScoresByProvince(province:str, db: Session = Depends(get_db)):
    return (
        db.query(ClusterScore)
        .join(Cluster, Cluster.id == ClusterScore.cluster_id)
        .filter(
            Cluster.top_provinces.any(province)
        )
        .order_by(
            ClusterScore.total_score.desc()
        )
        .all()
    )

@router.get('/recompute')
async def recomputeScores(db: Session = Depends(get_db)):
    serv = ScorerService(db)
    res = serv.scoreAllClusters()

    return {"message": "Scores recomputed", "count": len(res)}