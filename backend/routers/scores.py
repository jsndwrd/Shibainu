from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import get_db
from models import ClusterScore
from schemas.score import (
    PriorityScoreRequest,
    PriorityScoreResponse,
    ScoreResponse,
)
from services.scorer import ScorerService, calculate_priority_score

router = APIRouter()


@router.get('/top', response_model=list[ScoreResponse])
async def getTopScores(db: Session = Depends(get_db)):
    return (db.query(ClusterScore).order_by(ClusterScore.total_score.desc()).limit(10).all())

    Formula:
    Priority Score = 35% GDI + 35% PAVI + 30% Asta Cita
    """
    return calculate_priority_score(
        report_count=payload.report_count,
        population=payload.population,
        unique_regions=payload.unique_regions,
        asta_cita=payload.asta_cita,
        asta_confidence=payload.asta_confidence,
        max_regions=payload.max_regions,
        max_reports_per_100k=payload.max_reports_per_100k,
    )


@router.get("/", response_model=list[ScoreResponse])
async def get_all_scores(db: Session = Depends(get_db)):
    return (
        db.query(ClusterScore)
        .order_by(ClusterScore.computed_at.desc())
        .all()
    )


@router.get("/top", response_model=list[ScoreResponse])
async def get_top_scores(limit: int = 10, db: Session = Depends(get_db)):
    service = ScorerService(db)
    return service.get_top_scores(limit=limit)


@router.post("/recompute")
async def recompute_scores(db: Session = Depends(get_db)):
    service = ScorerService(db)
    results = service.score_all_clusters()

    return {
        "message": "Scores recomputed",
        "count": len(results),
    }


@router.post("/clusters/{cluster_id}/recompute", response_model=ScoreResponse)
async def recompute_cluster_score(cluster_id: UUID, db: Session = Depends(get_db)):
    service = ScorerService(db)
    score = service.score_cluster(cluster_id)

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cluster not found",
        )

    return score