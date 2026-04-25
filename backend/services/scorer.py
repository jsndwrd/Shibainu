from sqlalchemy.orm import Session
from models import ClusterScore, Cluster

class ScorerService:
    def __init__(self, db: Session):
        self.db = db

    def computePriorityScore(self, cluster):
        volume = min(cluster.member_count / 100, 1.0) * 40
        urgency = (cluster.avg_urgency / 5) * 40
        geo = min(len(cluster.top_provinces) / 10, 1.0) * 10
        impact = 10

        total = volume + urgency + geo + impact

        return {
            "volume_score": volume,
            "urgency_score": urgency,
            "geo_spread_score": geo,
            "impact_score": impact,
            "total_score": total,
        }

    def scoreCluster(self, cluster_id):
        cluster = (
            self.db.query(Cluster)
            .filter(Cluster.id == cluster_id)
            .first()
        )

        if not cluster:
            return None

        result = self.compute_priority_score(cluster)

        score = ClusterScore(
            cluster_id=cluster.id,
            volume_score=result["volume_score"],
            urgency_score=result["urgency_score"],
            geo_spread_score=result["geo_spread_score"],
            impact_score=result["impact_score"],
            total_score=result["total_score"],
            equity_adjusted_score=result["total_score"],
        )

        self.db.add(score)
        self.db.commit()
        self.db.refresh(score)

        return score

    def scoreAllClusters(self):
        clusters = self.db.query(Cluster).all()
        res = []

        for c in clusters:
            res.append(self.scoreCluster(c.id))
        
        return res