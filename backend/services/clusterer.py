from typing import List, Optional

from sqlalchemy.orm import Session

from models import Cluster


def cosine_similarity(a: List[float], b: List[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot / (norm_a * norm_b)


def update_centroid(old_centroid: List[float], new_embedding: List[float], old_count: int) -> List[float]:
    if not old_centroid:
        return new_embedding

    new_count = old_count + 1

    return [
        ((old_value * old_count) + new_value) / new_count
        for old_value, new_value in zip(old_centroid, new_embedding)
    ]


class ClustererService:
    def __init__(self, db: Session):
        self.db = db

    def assign_cluster(
        self,
        embedding,
        category,
        province,
        impact_scope,
        asta_cita,
        asta_confidence,
        population: Optional[int] = None,
        similarity_threshold: float = 0.78,
    ):
        candidates = (
            self.db.query(Cluster)
            .filter(Cluster.category == category)
            .all()
        )

        best_cluster = None
        best_similarity = 0.0

        for cluster in candidates:
            sim = cosine_similarity(embedding, cluster.centroid or [])

            if sim > best_similarity:
                best_similarity = sim
                best_cluster = cluster

        if best_cluster and best_similarity >= similarity_threshold:
            old_count = best_cluster.member_count or 1

            best_cluster.centroid = update_centroid(
                old_centroid=best_cluster.centroid or [],
                new_embedding=embedding,
                old_count=old_count,
            )

            best_cluster.member_count = old_count + 1

            provinces = best_cluster.top_provinces or []
            if province and province not in provinces:
                provinces.append(province)
            best_cluster.top_provinces = provinces

            best_cluster.dominant_asta_cita = asta_cita
            best_cluster.asta_confidence = max(
                float(best_cluster.asta_confidence or 0.0),
                float(asta_confidence or 0.0),
            )

            if impact_scope:
                best_cluster.dominant_impact_scope = impact_scope

            if population:
                current_population = best_cluster.population or 0
                best_cluster.population = max(current_population, int(population))

            self.db.commit()
            self.db.refresh(best_cluster)

            return best_cluster

        return self.create_cluster(
            category=category,
            province=province,
            impact_scope=impact_scope,
            embedding=embedding,
            asta_cita=asta_cita,
            asta_confidence=asta_confidence,
            population=population,
        )

    def create_cluster(
        self,
        category,
        province,
        impact_scope,
        embedding,
        asta_cita,
        asta_confidence,
        population: Optional[int] = None,
    ):
        cluster = Cluster(
            label=f"Cluster {category}",
            category=category,
            centroid=embedding,
            member_count=1,
            top_provinces=[province] if province else [],
            population=population or 100000,
            dominant_asta_cita=asta_cita,
            asta_confidence=asta_confidence,
            sub_topics=[],
            dominant_impact_scope=impact_scope,
            metadata_json={},
        )

        self.db.add(cluster)
        self.db.commit()
        self.db.refresh(cluster)

        return cluster

    def recompute_clusters(self):
        return True

    # Compatibility alias
    def assignCluster(self, *args, **kwargs):
        return self.assign_cluster(*args, **kwargs)

    def createCluster(self, *args, **kwargs):
        return self.create_cluster(*args, **kwargs)

    def recomputeClusters(self):
        return self.recompute_clusters()