import math
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models import Cluster, ClusterScore


GDI_WEIGHT = 0.35
PAVI_WEIGHT = 0.35
ASTA_CITA_WEIGHT = 0.30


def clamp(value: float, min_value: float = 0.0, max_value: float = 1.0) -> float:
    return max(min_value, min(float(value), max_value))


def normalize_gdi(unique_regions: int, max_regions: int = 10) -> float:
    if unique_regions is None or unique_regions <= 0:
        return 0.0

    if max_regions <= 0:
        max_regions = 10

    return clamp(unique_regions / max_regions)


def calculate_reports_per_100k(report_count: int, population: int) -> float:
    if report_count is None or report_count <= 0:
        return 0.0

    if population is None or population <= 0:
        return 0.0

    return (report_count / population) * 100000


def normalize_pavi(
    report_count: int,
    population: int,
    max_reports_per_100k: float = 30.0,
) -> Dict[str, float]:
    reports_per_100k = calculate_reports_per_100k(
        report_count=report_count,
        population=population,
    )

    if max_reports_per_100k <= 0:
        max_reports_per_100k = 30.0

    pavi_score = math.log1p(reports_per_100k) / math.log1p(max_reports_per_100k)

    return {
        "reports_per_100k": round(reports_per_100k, 4),
        "pavi_score": round(clamp(pavi_score), 4),
    }


def normalize_asta_cita(
    asta_cita: Optional[str],
    asta_confidence: Optional[float] = None,
) -> float:
    if asta_confidence is not None:
        return clamp(float(asta_confidence))

    if not asta_cita:
        return 0.30

    asta_text = str(asta_cita).strip().lower()

    if asta_text in ["unknown", "misi unknown", "none", "-", ""]:
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


def should_trigger_policy_brief(priority_score: float) -> bool:
    return priority_score >= 65


def calculate_priority_score(
    report_count: int,
    population: int,
    unique_regions: int,
    asta_cita: Optional[str],
    asta_confidence: Optional[float] = None,
    max_regions: int = 10,
    max_reports_per_100k: float = 30.0,
) -> Dict[str, Any]:
    gdi_score = normalize_gdi(
        unique_regions=unique_regions,
        max_regions=max_regions,
    )

    pavi_result = normalize_pavi(
        report_count=report_count,
        population=population,
        max_reports_per_100k=max_reports_per_100k,
    )

    pavi_score = pavi_result["pavi_score"]

    asta_cita_score = normalize_asta_cita(
        asta_cita=asta_cita,
        asta_confidence=asta_confidence,
    )

    normalized_score = (
        GDI_WEIGHT * gdi_score
        + PAVI_WEIGHT * pavi_score
        + ASTA_CITA_WEIGHT * asta_cita_score
    )

    priority_score = round(normalized_score * 100, 2)

    return {
        "priority_score": priority_score,
        "priority_level": get_priority_level(priority_score),
        "should_generate_brief": should_trigger_policy_brief(priority_score),
        "normalized_score": round(normalized_score, 4),
        "components": {
            "gdi_score": round(gdi_score, 4),
            "pavi_score": round(pavi_score, 4),
            "asta_cita_score": round(asta_cita_score, 4),
        },
        "raw_metrics": {
            "report_count": report_count,
            "population": population,
            "reports_per_100k": pavi_result["reports_per_100k"],
            "unique_regions": unique_regions,
            "asta_cita": asta_cita,
            "asta_confidence": asta_confidence,
            "max_regions": max_regions,
            "max_reports_per_100k": max_reports_per_100k,
        },
        "weights": {
            "gdi": GDI_WEIGHT,
            "pavi": PAVI_WEIGHT,
            "asta_cita": ASTA_CITA_WEIGHT,
        },
    }


class ScorerService:
    def __init__(self, db: Session):
        self.db = db

    def compute_priority_score(self, cluster: Cluster) -> Dict[str, Any]:
        unique_regions = len(cluster.top_provinces or [])
        population = getattr(cluster, "population", None) or 100000

        return calculate_priority_score(
            report_count=cluster.member_count or 0,
            population=population,
            unique_regions=unique_regions,
            asta_cita=cluster.dominant_asta_cita,
            asta_confidence=cluster.asta_confidence,
            max_regions=10,
            max_reports_per_100k=30.0,
        )

    def computePriorityScore(self, cluster: Cluster) -> Dict[str, Any]:
        return self.compute_priority_score(cluster)

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
        raw_metrics = result["raw_metrics"]

        score = ClusterScore(
            cluster_id=cluster.id,
            gdi_score=components["gdi_score"],
            pavi_score=components["pavi_score"],
            asta_cita_score=components["asta_cita_score"],
            reports_per_100k=raw_metrics["reports_per_100k"],
            population=raw_metrics["population"],
            total_score=result["priority_score"],
            priority_level=result["priority_level"],
            should_generate_brief=result["should_generate_brief"],
        )

        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)

        return score

    def scoreCluster(self, cluster_id):
        return self.score_cluster(cluster_id)

    def score_all_clusters(self):
        clusters = self.db.query(Cluster).all()
        results = []

        for cluster in clusters:
            score = self.score_cluster(cluster.id)
            if score:
                results.append(score)

        return results

    def scoreAllClusters(self):
        return self.score_all_clusters()

    def get_top_scores(self, limit: int = 10):
        return (
            self.db.query(ClusterScore)
            .order_by(ClusterScore.total_score.desc())
            .limit(limit)
            .all()
        )