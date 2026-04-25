from sqlalchemy.orm import Session
from services.cleaner import CleanerService
from services.embedder import EmbedderService
from services.clusterer import ClustererService
from services.scorer import ScorerService
from models import Aspiration

class AspirationService:
    def __init__(self, db: Session):
        self.db = db
        self.cleaner = CleanerService()
        self.embedder = EmbedderService()

    def createAspiration(self, citizen_id, payload):
        clean = self.cleaner.cleanDesc(payload.description)
        pred = self.embedder.predictAll(clean)
        clusterServ = ClustererService(self.db)

        cluster = clusterServ.assign_cluster(
            embedding=pred["embedding"],
            category=pred["category"],
            urgency=pred["urgency"],
            province=payload.province,
            impact_scope=payload.impact_scope,
        )

        aspiration = Aspiration(
            citizen_id=citizen_id,
            description=payload.description,
            cleaned_description=clean,
            category_user_input=payload.category,
            predicted_category=pred["category"],
            urgency_user_input=payload.urgency,
            predicted_urgency=pred["urgency"],
            province=payload.province,
            regency=payload.regency,
            impact_scope=payload.impact_scope,
            target_level=payload.target_level,
            embedding=pred["embedding"],
            cluster_id=cluster.id,
            status="processed"
        )

        self.db.add(aspiration)
        self.db.commit()
        self.db.refresh(aspiration)

        scorer = ScorerService(self.db)
        scorer.scoreCluster(cluster.id)

        return aspiration
    
    def getMyAspiration(self, citizen_id):
        return (self.db.query(Aspiration).filter(Aspiration.citizen_id == citizen_id).order_by(Aspiration.submitted_at.desc()).all())

    def getAllAspirations(self):
        return (self.db.query(Aspiration).order_by(Aspiration.submitted_at.desc()).all())

    def getAspirationById(self, aspiration_id):
        return (self.db.query(Aspiration).filter(Aspiration.id == aspiration_id).first())

    def updateStatus(self, aspiration_id, status):
        asp = self.getAspirationById(aspiration_id)

        if not asp:
            return None

        asp.status = status
        self.db.commit()
        self.db.refresh(asp)

        return asp