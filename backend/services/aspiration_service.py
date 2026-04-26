from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from models import Aspiration
from services.cleaner import CleanerService
from services.clusterer import ClustererService
from services.embedder import EmbedderService
from services.policy_level_classifier import PolicyLevelClassifier
from services.scorer import ScorerService


class AspirationService:
    def __init__(self, db: Session):
        self.db = db
        self.cleaner = CleanerService()
        self.embedder = EmbedderService(db)
        self.policy_classifier = PolicyLevelClassifier()

    def _recalculateCluster(self, cluster_id):
        from models import Cluster, Citizen

        cluster = (
            self.db.query(Cluster)
            .filter(Cluster.id == cluster_id)
            .first()
        )

        if not cluster:
            return None

        aspirations = (
            self.db.query(Aspiration)
            .filter(Aspiration.cluster_id == cluster_id)
            .all()
        )

        member_count = len(aspirations)

        provinces = []

        # Prioritas utama: ambil dari aspiration.province
        for aspiration in aspirations:
            province = getattr(aspiration, "province", None)

            if province and province not in provinces:
                provinces.append(province)

        # Fallback: kalau aspiration.province kosong, ambil dari citizen.province
        if not provinces:
            citizen_ids = [
                aspiration.citizen_id
                for aspiration in aspirations
                if aspiration.citizen_id
            ]

            if citizen_ids:
                citizens = (
                    self.db.query(Citizen)
                    .filter(Citizen.id.in_(citizen_ids))
                    .all()
                )

                for citizen in citizens:
                    province = getattr(citizen, "province", None)

                    if province and province not in provinces:
                        provinces.append(province)

        self._setIfExists(cluster, "member_count", member_count)
        self._setIfExists(cluster, "top_provinces", provinces[:3])

        if hasattr(cluster, "population") and not cluster.population:
            cluster.population = 100000

        self.db.commit()
        self.db.refresh(cluster)

        return cluster

    def createAspiration(self, citizen_id, payload):
        try:
            clean_text = self.cleaner.cleanDesc(payload.description)

            prediction = self._safePredict(clean_text, payload)

            similar_report_count = self._countSimilarReports(
                category=prediction["category"],
                province=payload.province,
            )

            unique_region_count = self._countUniqueRegions(
                category=prediction["category"],
            )

            policy_result = self.policy_classifier.classify(
                text=clean_text,
                category=prediction["category"],
                asta_cita=prediction["asta_cita"],
                report_count=similar_report_count,
                unique_regions=unique_region_count,
            )

            policy_level = policy_result.get("policy_level", "operational")
            routing_target = policy_result.get(
                "routing_target",
                "operational_ticket",
            )

            cluster = None

            if policy_level == "strategic":
                cluster = self._assignStrategicCluster(
                    prediction=prediction,
                    payload=payload,
                )

            aspiration = Aspiration()

            self._setIfExists(aspiration, "citizen_id", citizen_id)
            self._setIfExists(aspiration, "description", payload.description)
            self._setIfExists(aspiration, "cleaned_description", clean_text)

            self._setIfExists(
                aspiration,
                "category_user_input",
                getattr(payload, "category", None),
            )
            self._setIfExists(
                aspiration,
                "predicted_category",
                prediction["category"],
            )
            self._setIfExists(
                aspiration,
                "category",
                prediction["category"],
            )
            self._setIfExists(
                aspiration,
                "category_confidence",
                prediction.get("category_confidence", 0.0),
            )

            self._setIfExists(
                aspiration,
                "predicted_asta_cita",
                prediction["asta_cita"],
            )
            self._setIfExists(
                aspiration,
                "asta_confidence",
                prediction.get("asta_confidence", 0.0),
            )

            self._setIfExists(aspiration, "policy_level", policy_level)
            self._setIfExists(
                aspiration,
                "policy_level_confidence",
                policy_result.get("confidence", 0.0),
            )
            self._setIfExists(
                aspiration,
                "policy_level_reason",
                policy_result.get("reason", ""),
            )
            self._setIfExists(aspiration, "routing_target", routing_target)

            self._setIfExists(aspiration, "province", payload.province)
            self._setIfExists(aspiration, "regency", payload.regency)
            self._setIfExists(aspiration, "impact_scope", payload.impact_scope)
            self._setIfExists(aspiration, "target_level", payload.target_level)

            self._setIfExists(aspiration, "embedding", prediction["embedding"])

            if cluster:
                self._setIfExists(aspiration, "cluster_id", cluster.id)
                self._setIfExists(aspiration, "status", "strategic")
            else:
                self._setIfExists(aspiration, "cluster_id", None)
                self._setIfExists(aspiration, "status", "operational")

            self.db.add(aspiration)
            self.db.commit()
            self.db.refresh(aspiration)

            if cluster:
                self._recalculateCluster(cluster.id)
                score_val = self._scoreStrategicCluster(cluster.id)
                self._syncAspirationPriorityScore(aspiration.id, score_val)

            return aspiration

        except Exception:
            self.db.rollback()
            raise

    def getMyAspiration(self, citizen_id):
        return (
            self.db.query(Aspiration)
            .filter(Aspiration.citizen_id == citizen_id)
            .order_by(Aspiration.submitted_at.desc())
            .all()
        )

    def getAllAspirations(self):
        return (
            self.db.query(Aspiration)
            .order_by(Aspiration.submitted_at.desc())
            .all()
        )

    def getAspirationById(self, aspiration_id):
        return (
            self.db.query(Aspiration)
            .filter(Aspiration.id == aspiration_id)
            .first()
        )

    def updateStatus(self, aspiration_id, status):
        aspiration = self.getAspirationById(aspiration_id)

        if not aspiration:
            return None

        aspiration.status = status

        self.db.commit()
        self.db.refresh(aspiration)

        return aspiration

    def _safePredict(self, clean_text: str, payload) -> Dict[str, Any]:
        prediction = self.embedder.predict_all(clean_text)

        if not isinstance(prediction, dict):
            prediction = {}

        category = (
            prediction.get("category")
            or getattr(payload, "category", None)
            or "Pelayanan Publik"
        )

        asta_cita = (
            prediction.get("asta_cita")
            or prediction.get("predicted_asta_cita")
            or "Asta Cita 7"
        )

        embedding = prediction.get("embedding")

        if embedding is None:
            embedding = []

        return {
            "category": category,
            "category_confidence": prediction.get("category_confidence", 0.0),
            "asta_cita": asta_cita,
            "asta_confidence": prediction.get("asta_confidence", 0.0),
            "embedding": embedding,
        }

    def _assignStrategicCluster(self, prediction: Dict[str, Any], payload):
        cluster_service = ClustererService(self.db)

        population = getattr(payload, "population", None)

        if not population:
            population = 100000

        return cluster_service.assign_cluster(
            embedding=prediction["embedding"],
            category=prediction["category"],
            province=payload.province,
            impact_scope=payload.impact_scope,
            asta_cita=prediction["asta_cita"],
            asta_confidence=prediction.get("asta_confidence", 0.0),
            population=population,
        )

    def _scoreStrategicCluster(self, cluster_id):
        from models import Cluster

        scorer = ScorerService(self.db)

        result = None

        if hasattr(scorer, "score_cluster"):
            result = scorer.score_cluster(cluster_id)
        elif hasattr(scorer, "scoreCluster"):
            result = scorer.scoreCluster(cluster_id)
        elif hasattr(scorer, "scoreAllClusters"):
            result = scorer.scoreAllClusters()

        score_value = self._extractScoreValue(result)

        cluster = (
            self.db.query(Cluster)
            .filter(Cluster.id == cluster_id)
            .first()
        )

        if cluster and score_value is not None:
            self._setIfExists(cluster, "priority_score", score_value)
            self.db.commit()
            self.db.refresh(cluster)

        return score_value


    def _extractScoreValue(self, result):
        if result is None:
            return 0

        if isinstance(result, dict):
            return (
                result.get("priority_score")
                or result.get("total_score")
                or result.get("score")
                or 0
            )

        if isinstance(result, list) and result:
            first = result[0]

            if isinstance(first, dict):
                return (
                    first.get("priority_score")
                    or first.get("total_score")
                    or first.get("score")
                    or 0
                )

        total_score = getattr(result, "total_score", None)

        if total_score is not None:
            return total_score

        priority_score = getattr(result, "priority_score", None)

        if priority_score is not None:
            return priority_score

        return 0


    def _syncAspirationPriorityScore(self, aspiration_id, score_value):
        aspiration = (
            self.db.query(Aspiration)
            .filter(Aspiration.id == aspiration_id)
            .first()
        )

        if not aspiration:
            return None

        self._setIfExists(aspiration, "priority_score", score_value or 0)

        self.db.commit()
        self.db.refresh(aspiration)

        return aspiration

    def _countSimilarReports(
        self,
        category: Optional[str],
        province: Optional[str],
    ) -> int:
        query = self.db.query(Aspiration)

        if hasattr(Aspiration, "predicted_category") and category:
            query = query.filter(Aspiration.predicted_category == category)

        if hasattr(Aspiration, "province") and province:
            query = query.filter(Aspiration.province == province)

        count = query.count()

        return count + 1

    def _countUniqueRegions(self, category: Optional[str]) -> int:
        if not hasattr(Aspiration, "province"):
            return 1

        query = self.db.query(Aspiration.province)

        if hasattr(Aspiration, "predicted_category") and category:
            query = query.filter(Aspiration.predicted_category == category)

        regions = {
            row[0]
            for row in query.all()
            if row and row[0]
        }

        return max(1, len(regions))

    def _setIfExists(self, model, field: str, value):
        if hasattr(model, field):
            setattr(model, field, value)