import os
import re
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from models import Cluster, PolicyBrief
from services.llm_service import LocalLLMService
from services.scorer import ScorerService


class BriefGeneratorService:
    def __init__(self, db: Session):
        self.db = db
        self.llm = LocalLLMService()

        self.base_dir = Path(__file__).resolve().parents[1]
        self.output_dir = self.base_dir / "generated_briefs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _safe_filename(self, text: str) -> str:
        text = text or "policy_brief"
        text = text.lower()
        text = re.sub(r"[^a-z0-9]+", "_", text)
        text = re.sub(r"_+", "_", text).strip("_")
        return text[:80] or "policy_brief"

    def build_prompt(self, cluster: Cluster, score: dict) -> str:
        components = score["components"]
        raw_metrics = score["raw_metrics"]

        provinces = ", ".join(cluster.top_provinces or [])
        if not provinces:
            provinces = "Tidak tersedia"

        return f"""
Buat POLICY BRIEF final dalam Bahasa Indonesia yang formal, jelas, dan siap dibaca oleh pemerintah daerah atau DPRD.

Gunakan data berikut. Jangan menambahkan data di luar input.

DATA CLUSTER ASPIRASI
- Judul isu: {cluster.label}
- Kategori isu: {cluster.category}
- Jumlah laporan serupa: {cluster.member_count}
- Jumlah wilayah terdampak: {len(cluster.top_provinces or [])}
- Wilayah utama: {provinces}
- Asta Cita terkait: {cluster.dominant_asta_cita or "Misi UNKNOWN"}
- Confidence Asta Cita: {cluster.asta_confidence}
- Priority Score: {score["priority_score"]}
- Priority Level: {score["priority_level"]}
- GDI Score: {components["gdi_score"]}
- PAVI Score: {components["pavi_score"]}
- Asta Cita Score: {components["asta_cita_score"]}
- Reports per 100.000 penduduk: {raw_metrics["reports_per_100k"]}
- Population basis: {raw_metrics["population"]}

FORMAT WAJIB OUTPUT MARKDOWN
# Policy Brief: [judul singkat]

## 1. Ringkasan Eksekutif
Tuliskan ringkasan inti isu, jumlah laporan, sebaran wilayah, kategori, dan relevansi Asta Cita.

## 2. Latar Belakang Isu
Jelaskan mengapa isu ini penting sebagai aspirasi publik.

## 3. Analisis Prioritas
Jelaskan Priority Score berdasarkan GDI, PAVI, dan Asta Cita. Gunakan angka yang tersedia.

## 4. Keterkaitan dengan Asta Cita
Jelaskan keterkaitan isu dengan Asta Cita terkait.

## 5. Dampak Kebijakan
Jelaskan dampak jika isu tidak ditindaklanjuti.

## 6. Rekomendasi Kebijakan
Buat 3 sampai 5 rekomendasi yang realistis, operasional, dan relevan.

## 7. Target Tindak Lanjut
Sebutkan siapa pihak yang sebaiknya menindaklanjuti secara umum, misalnya dinas teknis, pemerintah daerah, DPRD, atau unit layanan.

ATURAN
- Jangan mengarang nama wilayah selain yang tersedia.
- Jangan mengarang angka baru.
- Jangan menyebut urgency karena sistem final tidak menggunakan urgency.
- Gunakan bahasa formal dan profesional.
- Maksimal 900 kata.
""".strip()

    def generate_template_brief(self, cluster: Cluster, score: dict) -> str:
        components = score["components"]
        raw_metrics = score["raw_metrics"]

        provinces = ", ".join(cluster.top_provinces or [])
        if not provinces:
            provinces = "Tidak tersedia"

        return f"""
# Policy Brief: {cluster.label}

## 1. Ringkasan Eksekutif

Isu ini masuk dalam kategori **{cluster.category}** dan dihimpun dari **{cluster.member_count} laporan warga** yang memiliki kemiripan substansi. Isu ini tersebar di **{len(cluster.top_provinces or [])} wilayah**, dengan wilayah utama: **{provinces}**.

Sistem mengaitkan isu ini dengan **{cluster.dominant_asta_cita or "Misi UNKNOWN"}** sebagai agenda pembangunan yang relevan. Berdasarkan perhitungan prioritas, isu ini memperoleh **Priority Score {score["priority_score"]}** dengan level **{score["priority_level"]}**.

## 2. Latar Belakang Isu

Aspirasi warga yang terkumpul menunjukkan adanya pola masalah yang perlu diperhatikan secara lebih terstruktur. Pengelompokan dilakukan berdasarkan kemiripan makna laporan, kategori isu, dan keterkaitan terhadap agenda pembangunan.

## 3. Analisis Prioritas

Priority Score dihitung menggunakan tiga komponen utama:

- **GDI Score**: {components["gdi_score"]}
- **PAVI Score**: {components["pavi_score"]}
- **Asta Cita Score**: {components["asta_cita_score"]}
- **Reports per 100.000 penduduk**: {raw_metrics["reports_per_100k"]}
- **Population Basis**: {raw_metrics["population"]}

GDI menunjukkan sebaran geografis isu. PAVI menunjukkan intensitas laporan relatif terhadap populasi. Asta Cita Score menunjukkan relevansi isu terhadap agenda pembangunan nasional.

## 4. Keterkaitan dengan Asta Cita

Isu ini dikaitkan dengan **{cluster.dominant_asta_cita or "Misi UNKNOWN"}**. Keterkaitan ini digunakan sebagai policy alignment layer agar aspirasi warga dapat diterjemahkan menjadi agenda kebijakan yang lebih mudah dipahami oleh pemerintah.

## 5. Dampak Kebijakan

Jika isu ini tidak ditindaklanjuti, potensi masalah dapat terus berkembang dan menurunkan kepercayaan publik terhadap respons pemerintah. Pola laporan yang terkumpul menunjukkan perlunya verifikasi dan tindak lanjut berbasis data.

## 6. Rekomendasi Kebijakan

1. Pemerintah daerah perlu melakukan verifikasi lapangan terhadap cluster isu ini.
2. Dinas teknis terkait perlu menyusun tindak lanjut sesuai kategori isu.
3. DPRD atau pemerintah daerah dapat menggunakan laporan ini sebagai bahan awal pembahasan kebijakan.
4. Sistem perlu terus memantau pertambahan laporan serupa untuk melihat perubahan prioritas.
5. Hasil tindak lanjut perlu dipublikasikan agar warga mengetahui status penyelesaian.

## 7. Target Tindak Lanjut

Isu ini dapat diteruskan kepada pemerintah daerah, dinas teknis terkait, dan DPRD sesuai kategori masalah serta wilayah terdampak.
        """.strip()

    def save_brief_file(self, brief: PolicyBrief, cluster: Cluster) -> str:
        filename_base = self._safe_filename(f"{cluster.category}_{cluster.label}_{brief.id}")
        file_path = self.output_dir / f"{filename_base}.md"

        file_path.write_text(brief.content, encoding="utf-8")

        return str(file_path)

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

        if self.llm.is_available():
            try:
                system = (
                    "Anda adalah analis kebijakan publik. "
                    "Tugas Anda adalah menyusun policy brief berbasis data aspirasi warga. "
                    "Anda harus faktual, formal, dan tidak boleh mengarang data di luar input."
                )
                prompt = self.build_prompt(cluster, score)
                content = self.llm.generate(prompt=prompt, system=system)
                generated_by = "ollama_local_llm"
            except Exception as e:
                print(f"[BriefGeneratorService] LLM failed, using template fallback. Error: {e}")
                content = self.generate_template_brief(cluster, score)
                generated_by = "template_fallback"
        else:
            content = self.generate_template_brief(cluster, score)
            generated_by = "template_fallback"

        brief = PolicyBrief(
            cluster_id=cluster.id,
            content=content,
            urgency_classification=score["priority_level"],
            generated_by=generated_by,
            member_count_at_generation=cluster.member_count,
            priority_score_at_generation=score["priority_score"],
        )

        self.db.add(brief)
        self.db.commit()
        self.db.refresh(brief)

        self.save_brief_file(brief, cluster)

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

    def getBriefFilePath(self, brief_id):
        brief = self.getBrief(brief_id)

        if not brief:
            return None

        cluster = (
            self.db.query(Cluster)
            .filter(Cluster.id == brief.cluster_id)
            .first()
        )

        if not cluster:
            return None

        filename_base = self._safe_filename(f"{cluster.category}_{cluster.label}_{brief.id}")
        file_path = self.output_dir / f"{filename_base}.md"

        if not file_path.exists():
            file_path.write_text(brief.content, encoding="utf-8")

        return file_path