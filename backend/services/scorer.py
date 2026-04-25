import math
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models import Cluster, ClusterScore


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(float(value), max_value))


def normalize_volume(report_count: int, max_report_count: int = 100) -> float:
    """
    Volume laporan serupa dalam satu cluster.
    Dipakai log scaling agar cluster besar tidak terlalu mendominasi.
    """
    if report_count is None or report_count <= 0:
        return 0.0

    if max_report_count <= 1:
        max_report_count = max(report_count, 2)

    score = math.log1p(report_count) / math.log1p(max_report_count)
    return clamp(score)


def normalize_spread(unique_regions: int, max_regions: int = 10) -> float:
    """
    Spread wilayah berdasarkan jumlah daerah/provinsi/kabupaten unik.
    """
    if unique_regions is None or unique_regions <= 0:
        return 0.0

    if max_regions <= 0:
        max_regions = 10

    score = unique_regions / max_regions
    return clamp(score)


def normalize_asta_cita(
    asta_cita: Optional[str],
    asta_confidence: Optional[float] = None,
) -> float:
    """
    Asta Cita sebagai policy relevance factor.
    Kalau confidence model ada, pakai confidence.
    Kalau tidak ada, fallback:
    - mapped Asta Cita = 0.75
    - unknown = 0.30
    """
    if asta_confidence is not None:
        return clamp(float(asta_confidence))

    if not asta_cita:
        return 0.30

    text = str(asta_cita).strip().lower()

    if text in ["unknown", "misi unknown", "none", "-", ""]:
        return 0.30

    return 0.75


def get_priority_level(priority_score: float) -> str:
    if priority_score >= 80:
        return "critical"
    if priority_score >= 65:
        return "high"
    if priority_score >= 45:
        return "medium"
    return "low"


def should_trigger_policy_brief(
    priority_score: float,
    report_count: int,
    unique_regions: int,
) -> bool:
    """
    Policy brief dibuat kalau skor tinggi,
    atau kalau laporan sudah banyak dan tersebar.
    """
    if priority_score >= 65:
        return True

    if report_count >= 20 and unique_regions >= 3:
        return True

    return False


def calculate_priority_score(
    report_count: int,
    unique_regions: int,
    asta_cita: Optional[str],
    asta_confidence: Optional[float] = None,
    max_report_count: int = 100,
    max_regions: int = 10,
) -> Dict[str, Any]:
    volume_score = normalize_volume(
        report_count=report_count,
        max_report_count=max_report_count,
    )

    spread_score = normalize_spread(
        unique_regions=unique_regions,
        max_regions=max_regions,
    )

    asta_cita_score = normalize_asta_cita(
        asta_cita=asta_cita,
        asta_confidence=asta_confidence,
    )

    normalized_score = (
        0.45 * volume_score
        + 0.35 * spread_score
        + 0.20 * asta_cita_score
    )

    priority_score = round(normalized_score * 100, 2)

    return {
        "priority_score": priority_score,
        "priority_level": get_priority_level(priority_score),
        "should_generate_brief": should_trigger_policy_brief(
            priority_score=priority_score,
            report_count=report_count,
            unique_regions=unique_regions,
        ),
        "normalized_score": round(normalized_score, 4),
        "components": {
            "volume_score": round(volume_score, 4),
            "spread_score": round(spread_score, 4),
            "asta_cita_score": round(asta_cita_score, 4),
        },
        "weights": {
            "volume": 0.45,
            "spread": 0.35,
            "asta_cita": 0.20,
        },
        "raw_inputs": {
            "report_count": report_count,
            "unique_regions": unique_regions,
            "asta_cita": asta_cita,
            "asta_confidence": asta_confidence,
            "max_report_count": max_report_count,
            "max_regions": max_regions,
        },
    }


class ScorerService:
    def __init__(self, db: Session):
        self.db = db

    def compute_priority_score(self, cluster: Cluster) -> Dict[str, Any]:
        unique_regions = len(cluster.top_provinces or [])

        return calculate_priority_score(
            report_count=cluster.member_count or 0,
            unique_regions=unique_regions,
            asta_cita=cluster.dominant_asta_cita,
            asta_confidence=cluster.asta_confidence,
            max_report_count=100,
            max_regions=10,
        )

    def score_cluster(self, cluster_id):
        cluster = (
            self.db.query(Cluster)
            .filter(Cluster.id == cluster_id)
            .first()
        )

        if not cluster:
            return None

        result = self.compute_priority_score(cluster)
        components = result["components"]

        score = ClusterScore(
            cluster_id=cluster.id,
            volume_score=components["volume_score"],
            spread_score=components["spread_score"],
            asta_cita_score=components["asta_cita_score"],
            total_score=result["priority_score"],
            priority_level=result["priority_level"],
            should_generate_brief=result["should_generate_brief"],
        )

        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)

        return score

    def score_all_clusters(self):
        clusters = self.db.query(Cluster).all()
        results = []

        for cluster in clusters:
            score = self.score_cluster(cluster.id)
            if score:
                results.append(score)

        return results

    def get_top_scores(self, limit: int = 10):
        return (
            self.db.query(ClusterScore)
            .order_by(ClusterScore.total_score.desc())
            .limit(limit)
            .all()
        )