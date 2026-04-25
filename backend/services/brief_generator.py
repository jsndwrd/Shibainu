from __future__ import annotations

import json
import re
from pathlib import Path
from uuid import uuid4

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

    def _set_if_exists(self, model, field: str, value):
        if hasattr(model, field):
            setattr(model, field, value)

    def _get_nested_value(
        self,
        data: dict,
        path: list[str],
        default=None,
    ):
        current = data

        for key in path:
            if not isinstance(current, dict):
                return default

            current = current.get(key)

            if current is None:
                return default

        return current

    def _normalize_brief_content(self, content) -> str:
        if content is None:
            return ""

        if isinstance(content, str):
            clean_content = content.strip()

            if clean_content == "[object Object]":
                return "Konten policy brief tidak valid karena LLM mengembalikan object yang belum dinormalisasi."

            return clean_content

        if isinstance(content, dict):
            for key in [
                "content",
                "summary",
                "text",
                "result",
                "message",
                "response",
                "output",
            ]:
                value = content.get(key)

                if isinstance(value, str):
                    return value.strip()

                if isinstance(value, dict) or isinstance(value, list):
                    return self._normalize_brief_content(value)

            return json.dumps(content, ensure_ascii=False, indent=2)

        if isinstance(content, list):
            return "\n\n".join(
                self._normalize_brief_content(item)
                for item in content
            ).strip()

        return str(content)

    def _safe_score_value(
        self,
        score: dict,
        key: str,
        default=0,
    ):
        if not isinstance(score, dict):
            return default

        return score.get(key, default)

    def _safe_components(self, score: dict) -> dict:
        if not isinstance(score, dict):
            return {}

        components = score.get("components")

        if isinstance(components, dict):
            return components

        return {}

    def _safe_raw_metrics(self, score: dict) -> dict:
        if not isinstance(score, dict):
            return {}

        raw_metrics = score.get("raw_metrics")

        if isinstance(raw_metrics, dict):
            return raw_metrics

        return {}

    def build_prompt(self, cluster: Cluster, score: dict) -> str:
        components = self._safe_components(score)
        raw_metrics = self._safe_raw_metrics(score)

        top_provinces = getattr(cluster, "top_provinces", None) or []
        provinces = ", ".join(top_provinces) if top_provinces else "Tidak tersedia"

        label = getattr(cluster, "label", "Isu Aspirasi Publik")
        category = getattr(cluster, "category", "Tidak tersedia")
        member_count = getattr(cluster, "member_count", 0)
        dominant_asta_cita = getattr(cluster, "dominant_asta_cita", None) or "Misi UNKNOWN"
        asta_confidence = getattr(cluster, "asta_confidence", 0)

        priority_score = self._safe_score_value(score, "priority_score", 0)
        priority_level = self._safe_score_value(score, "priority_level", "Tidak tersedia")

        gdi_score = components.get("gdi_score", 0)
        pavi_score = components.get("pavi_score", 0)
        asta_cita_score = components.get("asta_cita_score", 0)

        reports_per_100k = raw_metrics.get("reports_per_100k", 0)
        population = raw_metrics.get("population", getattr(cluster, "population", 0))

        return f"""
Buat POLICY BRIEF final dalam Bahasa Indonesia yang formal, jelas, dan siap dibaca oleh pemerintah daerah atau DPRD.

Gunakan data berikut. Jangan menambahkan data di luar input.

DATA CLUSTER ASPIRASI
- Judul isu: {label}
- Kategori isu: {category}
- Jumlah laporan serupa: {member_count}
- Jumlah wilayah terdampak: {len(top_provinces)}
- Wilayah utama: {provinces}
- Asta Cita terkait: {dominant_asta_cita}
- Confidence Asta Cita: {asta_confidence}
- Priority Score: {priority_score}
- Priority Level: {priority_level}
- GDI Score: {gdi_score}
- PAVI Score: {pavi_score}
- Asta Cita Score: {asta_cita_score}
- Reports per 100.000 penduduk: {reports_per_100k}
- Population basis: {population}

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
        components = self._safe_components(score)
        raw_metrics = self._safe_raw_metrics(score)

        top_provinces = getattr(cluster, "top_provinces", None) or []
        provinces = ", ".join(top_provinces) if top_provinces else "Tidak tersedia"

        label = getattr(cluster, "label", "Isu Aspirasi Publik")
        category = getattr(cluster, "category", "Tidak tersedia")
        member_count = getattr(cluster, "member_count", 0)
        dominant_asta_cita = getattr(cluster, "dominant_asta_cita", None) or "Misi UNKNOWN"

        priority_score = self._safe_score_value(score, "priority_score", 0)
        priority_level = self._safe_score_value(score, "priority_level", "Tidak tersedia")

        gdi_score = components.get("gdi_score", 0)
        pavi_score = components.get("pavi_score", 0)
        asta_cita_score = components.get("asta_cita_score", 0)

        reports_per_100k = raw_metrics.get("reports_per_100k", 0)
        population = raw_metrics.get("population", getattr(cluster, "population", 0))

        return f"""
# Policy Brief: {label}

## 1. Ringkasan Eksekutif

Isu ini masuk dalam kategori **{category}** dan dihimpun dari **{member_count} laporan warga** yang memiliki kemiripan substansi. Isu ini tersebar di **{len(top_provinces)} wilayah**, dengan wilayah utama: **{provinces}**.

Sistem mengaitkan isu ini dengan **{dominant_asta_cita}** sebagai agenda pembangunan yang relevan. Berdasarkan perhitungan prioritas, isu ini memperoleh **Priority Score {priority_score}** dengan level **{priority_level}**.

## 2. Latar Belakang Isu

Aspirasi warga yang terkumpul menunjukkan adanya pola masalah yang perlu diperhatikan secara lebih terstruktur. Pengelompokan dilakukan berdasarkan kemiripan makna laporan, kategori isu, dan keterkaitan terhadap agenda pembangunan.

## 3. Analisis Prioritas

Priority Score dihitung menggunakan tiga komponen utama:

- **GDI Score**: {gdi_score}
- **PAVI Score**: {pavi_score}
- **Asta Cita Score**: {asta_cita_score}
- **Reports per 100.000 penduduk**: {reports_per_100k}
- **Population Basis**: {population}

GDI menunjukkan sebaran geografis isu. PAVI menunjukkan intensitas laporan relatif terhadap populasi. Asta Cita Score menunjukkan relevansi isu terhadap agenda pembangunan nasional.

## 4. Keterkaitan dengan Asta Cita

Isu ini dikaitkan dengan **{dominant_asta_cita}**. Keterkaitan ini digunakan sebagai policy alignment layer agar aspirasi warga dapat diterjemahkan menjadi agenda kebijakan yang lebih mudah dipahami oleh pemerintah.

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
        content = self._normalize_brief_content(getattr(brief, "content", ""))

        filename_base = self._safe_filename(
            f"{getattr(cluster, 'category', 'kategori')}_{getattr(cluster, 'label', 'cluster')}_{brief.id}"
        )

        file_path = self.output_dir / f"{filename_base}.md"
        file_path.write_text(content, encoding="utf-8")

        return str(file_path)

    def _create_policy_brief(
        self,
        cluster: Cluster,
        content,
        priority_level: str,
        generated_by: str,
        priority_score: float,
    ) -> PolicyBrief:
        normalized_content = self._normalize_brief_content(content)

        brief = PolicyBrief()

        self._set_if_exists(brief, "id", uuid4())
        self._set_if_exists(brief, "cluster_id", cluster.id)
        self._set_if_exists(brief, "content", normalized_content)
        self._set_if_exists(brief, "urgency_classification", priority_level)
        self._set_if_exists(brief, "generated_by", generated_by)

        self._set_if_exists(
            brief,
            "member_count_at_generation",
            getattr(cluster, "member_count", 0) or 0,
        )

        self._set_if_exists(
            brief,
            "priority_score_at_generation",
            priority_score or 0,
        )

        self.db.add(brief)
        self.db.commit()
        self.db.refresh(brief)

        return brief

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

        priority_score = self._safe_score_value(score, "priority_score", 0)
        priority_level = self._safe_score_value(score, "priority_level", "Tidak tersedia")

        if self.llm.is_available():
            try:
                system = (
                    "Anda adalah analis kebijakan publik. "
                    "Tugas Anda adalah menyusun policy brief berbasis data aspirasi warga. "
                    "Anda harus faktual, formal, dan tidak boleh mengarang data di luar input."
                )

                prompt = self.build_prompt(cluster, score)

                raw_content = self.llm.generate(
                    prompt=prompt,
                    system=system,
                )

                content = self._normalize_brief_content(raw_content)
                generated_by = "ollama_local_llm"

                if not content or content == "[object Object]":
                    content = self.generate_template_brief(cluster, score)
                    generated_by = "template_fallback"

            except Exception as e:
                print(
                    "[BriefGeneratorService] LLM failed, using template fallback. "
                    f"Error: {e}"
                )

                content = self.generate_template_brief(cluster, score)
                generated_by = "template_fallback"
        else:
            content = self.generate_template_brief(cluster, score)
            generated_by = "template_fallback"

        brief = self._create_policy_brief(
            cluster=cluster,
            content=content,
            priority_level=priority_level,
            generated_by=generated_by,
            priority_score=priority_score,
        )

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

        filename_base = self._safe_filename(
            f"{getattr(cluster, 'category', 'kategori')}_{getattr(cluster, 'label', 'cluster')}_{brief.id}"
        )

        file_path = self.output_dir / f"{filename_base}.md"

        if not file_path.exists():
            content = self._normalize_brief_content(
                getattr(brief, "content", "")
            )
            file_path.write_text(content, encoding="utf-8")

        return file_path