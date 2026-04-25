from sqlalchemy.orm import Session
from models import Cluster

class ClustererService:
    def __init__(self, db: Session):
        self.db = db

    def assignCluster(self, embedding, category, urgency, province, impact_scope):
        cluster = (
            self.db.query(Cluster)
            .filter(Cluster.category == category)
            .first()
        )

        if cluster:
            cluster.member_count += 1
            cluster.avg_urgency = (
                (cluster.avg_urgency * (cluster.member_count - 1))
                + urgency
            ) / cluster.member_count

            self.db.commit()
            self.db.refresh(cluster)
            return cluster

        return self.create_cluster(
            category,
            urgency,
            province,
            impact_scope,
            embedding
        )
    
    def createCluster(self, category, urgency, province, impact_scope, embedding):
        cluster = Cluster(
            label=f"Cluster {category}",
            category=category,
            centroid=embedding,
            member_count=1,
            top_provinces=[province],
            avg_urgency=float(urgency),
            urgency_dist={str(urgency): 1},
            sub_topics=[],
            dominant_impact_scope=impact_scope
        )

        self.db.add(cluster)
        self.db.commit()
        self.db.refresh(cluster)

        return cluster

    def recomputeClusters(self):
        return True