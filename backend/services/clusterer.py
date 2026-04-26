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

    def _set_if_exists(self, model, field: str, value):
        if hasattr(model, field):
            setattr(model, field, value)

    def _normalize_embedding(self, embedding):
        if not embedding:
            return []

        return [float(value) for value in embedding]
    
    def _find_existing_cluster(
    self,
    category,
    impact_scope,
    asta_cita,
):
        query = self.db.query(Cluster).filter(Cluster.category == category)

        if hasattr(Cluster, "dominant_asta_cita") and asta_cita:
            query = query.filter(Cluster.dominant_asta_cita == asta_cita)

        if hasattr(Cluster, "dominant_impact_scope") and impact_scope:
            query = query.filter(Cluster.dominant_impact_scope == impact_scope)

        cluster = (
            query
            .order_by(Cluster.created_at.asc())
            .first()
        )

        return cluster


    def _normalize_embedding(self, embedding):
        if not embedding:
            return []

        return [float(value) for value in embedding]


    def _set_if_exists(self, model, field: str, value):
        if hasattr(model, field):
            setattr(model, field, value)


    def _update_cluster_metadata(
        self,
        cluster,
        embedding,
        province,
        impact_scope,
        asta_cita,
        asta_confidence,
        population,
    ):
        top_provinces = getattr(cluster, "top_provinces", None) or []

        if province and province not in top_provinces:
            top_provinces.append(province)

        member_count = int(getattr(cluster, "member_count", 0) or 0)

        old_centroid = getattr(cluster, "centroid", None) or []
        new_centroid = self._merge_centroid(
            old_centroid=old_centroid,
            new_embedding=embedding,
            old_count=member_count,
        )

        self._set_if_exists(cluster, "centroid", new_centroid)
        self._set_if_exists(cluster, "top_provinces", top_provinces[:3])
        self._set_if_exists(cluster, "population", population or 100000)
        self._set_if_exists(cluster, "dominant_asta_cita", asta_cita)
        self._set_if_exists(cluster, "asta_confidence", asta_confidence or 0)
        self._set_if_exists(cluster, "dominant_impact_scope", impact_scope)

        self.db.flush()

        return cluster


    def _merge_centroid(
        self,
        old_centroid,
        new_embedding,
        old_count,
    ):
        old_centroid = self._normalize_embedding(old_centroid)
        new_embedding = self._normalize_embedding(new_embedding)

        if not old_centroid:
            return new_embedding

        if len(old_centroid) != len(new_embedding):
            return new_embedding

        total_count = max(old_count + 1, 1)

        return [
            ((old_centroid[i] * old_count) + new_embedding[i]) / total_count
            for i in range(len(new_embedding))
        ]

    def assign_cluster(
    self,
    embedding,
    category,
    province,
    impact_scope,
    asta_cita,
    asta_confidence,
    population,
):
        embedding = self._normalize_embedding(embedding)

        existing_cluster = self._find_existing_cluster(
            category=category,
            impact_scope=impact_scope,
            asta_cita=asta_cita,
        )

        if existing_cluster:
            self._update_cluster_metadata(
                cluster=existing_cluster,
                embedding=embedding,
                province=province,
                impact_scope=impact_scope,
                asta_cita=asta_cita,
                asta_confidence=asta_confidence,
                population=population,
            )

            return existing_cluster

        clusters = (
            self.db.query(Cluster)
            .filter(Cluster.category == category)
            .all()
        )

        best_cluster = None
        best_score = 0

        for cluster in clusters:
            centroid = getattr(cluster, "centroid", None) or []

            if not centroid:
                continue

            sim = cosine_similarity(embedding, centroid)

            if sim > best_score:
                best_score = sim
                best_cluster = cluster

        if best_cluster and best_score >= 0.75:
            self._update_cluster_metadata(
                cluster=best_cluster,
                embedding=embedding,
                province=province,
                impact_scope=impact_scope,
                asta_cita=asta_cita,
                asta_confidence=asta_confidence,
                population=population,
            )

            return best_cluster

        return self.create_cluster(
            category=category,
            embedding=embedding,
            province=province,
            impact_scope=impact_scope,
            asta_cita=asta_cita,
            asta_confidence=asta_confidence,
            population=population,
        )

    def create_cluster(
    self,
    category,
    embedding,
    province,
    impact_scope,
    asta_cita,
    asta_confidence,
    population,
):
        cluster = Cluster()

        self._set_if_exists(cluster, "label", f"Cluster {category}")
        self._set_if_exists(cluster, "category", category)
        self._set_if_exists(cluster, "centroid", self._normalize_embedding(embedding))
        self._set_if_exists(cluster, "member_count", 0)
        self._set_if_exists(cluster, "avg_urgency", 0)
        self._set_if_exists(cluster, "top_provinces", [province] if province else [])
        self._set_if_exists(cluster, "priority_score", 0)
        self._set_if_exists(cluster, "population", population or 100000)
        self._set_if_exists(cluster, "dominant_asta_cita", asta_cita)
        self._set_if_exists(cluster, "asta_confidence", asta_confidence or 0)
        self._set_if_exists(cluster, "dominant_impact_scope", impact_scope)
        self._set_if_exists(cluster, "metadata_json", {})
        self._set_if_exists(cluster, "sub_topics", [])
        self._set_if_exists(
            cluster,
            "urgency_dist",
            {
                "1": 0,
                "2": 0,
                "3": 0,
                "4": 0,
                "5": 0,
            },
        )

        self.db.add(cluster)
        self.db.flush()

        return cluster
    
    def recompute_clusters(self):
        return True

    def assignCluster(self, *args, **kwargs):
        return self.assign_cluster(*args, **kwargs)

    def createCluster(self, *args, **kwargs):
        return self.create_cluster(*args, **kwargs)

    def recomputeClusters(self):
        return self.recompute_clusters()