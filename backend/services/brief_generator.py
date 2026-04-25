from sqlalchemy.orm import Session
from models import PolicyBrief, Cluster
from services import ScorerService

class BriefGeneratorService:
    def __init__(self, db: Session):
        self.db = db
    
    def generateBrief(self, cluster_id):
        cluster = (
            self.db.query(Cluster)
            .filter(Cluster.id == cluster_id)
            .first()
        )

        if not cluster:
            return None

        scorer = ScorerService(self.db)
        score = scorer.compute_priority_score(cluster)

        content = f"""
                    Policy Brief: {cluster.label}

                    Kategori: {cluster.category}
                    Jumlah Aspirasi: {cluster.member_count}
                    Urgensi Rata-rata: {cluster.avg_urgency:.2f}
                    Priority Score: {score["total_score"]:.2f}

                    Rekomendasi:
                    BELOM
                    """

        brief = PolicyBrief(
            cluster_id=cluster.id,
            content=content.strip(),
            urgency_classification="Segera",
            generated_by="system",
            member_count_at_generation=cluster.member_count,
            priority_score_at_generation=score["total_score"],
        )

        self.db.add(brief)
        self.db.commit()
        self.db.refresh(brief)

        return brief


    def generateMany(self, cluster_ids):
        return [self.generateBrief(c_id) for c_id in cluster_ids]

    def getBrief(self, brief_id):
        return (self.db.query(PolicyBrief).filter(PolicyBrief.id == brief_id).first())