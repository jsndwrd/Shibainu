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

        components = score["components"]
        raw_metrics = score["raw_metrics"]

        content = f"""
POLICY BRIEF ASPIRASI PUBLIK

Judul Isu:
{cluster.label}

Kategori:
{cluster.category}

Asta Cita Terkait:
{cluster.dominant_asta_cita or "Misi UNKNOWN"}

Ringkasan Isu:
Terdapat {cluster.member_count} laporan warga yang memiliki kemiripan isu dan masuk ke dalam cluster {cluster.category}. Isu ini tersebar di {len(cluster.top_provinces or [])} wilayah dan memiliki keterkaitan dengan {cluster.dominant_asta_cita or "Misi UNKNOWN"}.

Hasil Prioritas:
Priority Score: {score["priority_score"]}
Priority Level: {score["priority_level"]}

Komponen Perhitungan:
- GDI Score: {components["gdi_score"]}
- PAVI Score: {components["pavi_score"]}
- Asta Cita Score: {components["asta_cita_score"]}
- Reports per 100.000 penduduk: {raw_metrics["reports_per_100k"]}
- Population Basis: {raw_metrics["population"]}

Analisis Kebijakan:
Priority score dihitung dari tiga sinyal utama. GDI menangkap sebaran geografis isu, PAVI menangkap intensitas laporan relatif terhadap jumlah penduduk, dan Asta Cita mengukur relevansi isu terhadap agenda pembangunan nasional.

Rekomendasi:
1. Pemerintah perlu melakukan verifikasi lapangan terhadap cluster isu ini.
2. Instansi terkait perlu menyusun tindak lanjut sesuai kategori isu dan wilayah terdampak.
3. Jika laporan terus bertambah, isu ini dapat dinaikkan sebagai agenda pembahasan kebijakan prioritas.
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