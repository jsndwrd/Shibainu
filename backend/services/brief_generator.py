from sqlalchemy.orm import Session

from models import Cluster, PolicyBrief
from services.scorer import ScorerService


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
POLICY BRIEF ASPIRASI PUBLIK

Judul Isu:
{cluster.label}

Kategori:
{cluster.category}

Asta Cita Terkait:
{cluster.dominant_asta_cita or "Misi UNKNOWN"}

Ringkasan Isu:
Terdapat {cluster.member_count} laporan warga yang memiliki kemiripan isu dan masuk ke dalam cluster {cluster.category}. Isu ini tersebar di {len(cluster.top_provinces or [])} wilayah.

Hasil Prioritas:
Priority Score: {score["priority_score"]}
Priority Level: {score["priority_level"]}

Komponen Perhitungan:
- Volume Score: {score["components"]["volume_score"]}
- Spread Score: {score["components"]["spread_score"]}
- Asta Cita Score: {score["components"]["asta_cita_score"]}

Analisis Kebijakan:
Isu ini diprioritaskan berdasarkan banyaknya laporan serupa, sebaran wilayah, dan relevansi terhadap Asta Cita. Dengan pendekatan ini, sistem tidak hanya melihat satu laporan individual, tetapi membaca pola aspirasi kolektif warga.

Rekomendasi:
1. Pemerintah daerah perlu melakukan verifikasi lapangan terhadap cluster isu ini.
2. Instansi terkait perlu menyusun tindak lanjut sesuai kategori isu.
3. Jika laporan terus meningkat, isu ini dapat dinaikkan sebagai agenda pembahasan kebijakan.
        """.strip()

        brief = PolicyBrief(
            cluster_id=cluster.id,
            content=content,
            urgency_classification=score["priority_level"],
            generated_by="system",
            member_count_at_generation=cluster.member_count,
            priority_score_at_generation=score["priority_score"],
        )

        self.db.add(brief)
        self.db.commit()
        self.db.refresh(brief)

        return brief

    def generateMany(self, cluster_ids):
        results = []

        for cluster_id in cluster_ids:
            brief = self.generateBrief(cluster_id)
            if brief:
                results.append(brief)

        return results

    def getBrief(self, brief_id):
        return (
            self.db.query(PolicyBrief)
            .filter(PolicyBrief.id == brief_id)
            .first()
        )

    def getAllBriefs(self):
        return (
            self.db.query(PolicyBrief)
            .order_by(PolicyBrief.generated_at.desc())
            .all()
        )