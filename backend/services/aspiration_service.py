from sqlalchemy.orm import Session

from models import Aspiration
from services.cleaner import CleanerService
from services.clusterer import ClustererService
from services.embedder import EmbedderService
from services.scorer import ScorerService


class AspirationService:
    def __init__(self, db: Session):
        self.db = db
        self.cleaner = CleanerService()
        self.embedder = EmbedderService(db)

    def createAspiration(self, citizen_id, payload):
        clean = self.cleaner.cleanDesc(payload.description)
        prediction = self.embedder.predict_all(clean)

        cluster_service = ClustererService(self.db)

        cluster = cluster_service.assign_cluster(
            embedding=prediction["embedding"],
            category=prediction["category"],
            province=payload.province,
            impact_scope=payload.impact_scope,
            asta_cita=prediction["asta_cita"],
            asta_confidence=prediction["asta_confidence"],
            population=getattr(payload, "population", 100000) or 100000,
        )

        aspiration = Aspiration(
            citizen_id=citizen_id,
            description=payload.description,
            cleaned_description=clean,
            category_user_input=payload.category,
            predicted_category=prediction["category"],
            predicted_asta_cita=prediction["asta_cita"],
            asta_confidence=prediction["asta_confidence"],
            province=payload.province,
            regency=payload.regency,
            impact_scope=payload.impact_scope,
            target_level=payload.target_level,
            embedding=prediction["embedding"],
            cluster_id=cluster.id,
            status="processed",
        )

        self.db.add(aspiration)
        self.db.commit()
        self.db.refresh(aspiration)

        scorer = ScorerService(self.db)
        scorer.score_cluster(cluster.id)

        return aspiration

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