from typing import Dict, List, Optional


class PolicyLevelClassifier:
    """
    Classifier awal untuk membedakan laporan operational vs strategic.

    Operational:
    - Masalah teknis.
    - Bisa langsung ditangani dinas/unit pelaksana.
    - Tidak perlu masuk pipeline policy brief.

    Strategic:
    - Masalah sistemik.
    - Berulang, lintas wilayah, atau menyangkut kebijakan/anggaran/program.
    - Masuk clustering, scoring, dan policy brief.
    """

    def __init__(self):
        self.strategic_keywords = [
            "kebijakan",
            "anggaran",
            "regulasi",
            "program",
            "pemerataan",
            "ketimpangan",
            "sistemik",
            "berulang",
            "menahun",
            "struktural",
            "akses layanan",
            "pelayanan publik",
            "tidak tepat sasaran",
            "distribusi",
            "banyak desa",
            "banyak kecamatan",
            "banyak wilayah",
            "beberapa desa",
            "beberapa kecamatan",
            "seluruh desa",
            "daerah terpencil",
            "kekurangan guru",
            "kekurangan dokter",
            "kekurangan tenaga medis",
            "akses pendidikan",
            "akses kesehatan",
            "prioritas pembangunan",
            "alokasi dana",
            "bantuan tidak merata",
            "infrastruktur desa",
        ]

        self.operational_keywords = [
            "mati",
            "rusak",
            "berlubang",
            "bocor",
            "tersumbat",
            "tidak menyala",
            "belum diangkut",
            "belum diperbaiki",
            "perlu diperbaiki",
            "butuh perbaikan",
            "lambat",
            "antri",
            "macet",
            "kotor",
            "penuh",
            "hilang",
            "pecah",
            "roboh",
            "lampu jalan",
            "sampah",
            "got",
            "selokan",
            "drainase",
            "pipa",
            "trotoar",
            "jalan berlubang",
        ]

    def _count_keywords(self, text: str, keywords: List[str]) -> int:
        return sum(1 for keyword in keywords if keyword in text)

    def classify(
        self,
        text: str,
        category: Optional[str] = None,
        asta_cita: Optional[str] = None,
        report_count: int = 1,
        unique_regions: int = 1,
    ) -> Dict:
        text = (text or "").lower()
        category = category or "unknown"
        asta_cita = asta_cita or "Misi UNKNOWN"

        strategic_score = self._count_keywords(text, self.strategic_keywords)
        operational_score = self._count_keywords(text, self.operational_keywords)

        reasons = []

        if strategic_score > 0:
            reasons.append("Teks mengandung indikasi isu sistemik atau kebijakan.")

        if operational_score > 0:
            reasons.append("Teks mengandung indikasi masalah teknis operasional.")

        # Kalau laporan serupa sudah banyak, naikkan strategic.
        if report_count >= 10:
            strategic_score += 2
            reasons.append("Jumlah laporan serupa cukup banyak sehingga berpotensi menjadi isu strategis.")

        # Kalau tersebar di banyak wilayah, naikkan strategic.
        if unique_regions >= 3:
            strategic_score += 2
            reasons.append("Isu muncul di beberapa wilayah sehingga berpotensi sistemik.")

        # Kata-kata kolektif atau lintas wilayah.
        collective_terms = [
            "warga kami",
            "banyak warga",
            "masyarakat",
            "beberapa wilayah",
            "banyak daerah",
            "seluruh wilayah",
            "lintas desa",
            "lintas kecamatan",
        ]

        if any(term in text for term in collective_terms):
            strategic_score += 1
            reasons.append("Aspirasi mengarah pada dampak kolektif masyarakat.")

        # Masalah yang sangat spesifik di satu titik biasanya operational.
        specific_location_terms = [
            "di depan rumah",
            "di depan gang",
            "rt",
            "rw",
            "depan sekolah",
            "depan pasar",
            "depan kantor",
            "satu titik",
        ]

        if any(term in text for term in specific_location_terms):
            operational_score += 1
            reasons.append("Aspirasi mengarah pada titik lokasi spesifik.")

        if strategic_score > operational_score:
            confidence = min(0.95, 0.65 + 0.07 * (strategic_score - operational_score))
            return {
                "policy_level": "strategic",
                "routing_target": "policy_priority_pipeline",
                "confidence": round(confidence, 4),
                "strategic_score": strategic_score,
                "operational_score": operational_score,
                "reason": " ".join(reasons) or "Aspirasi menunjukkan karakter isu strategis.",
            }

        confidence = min(0.95, 0.65 + 0.07 * (operational_score - strategic_score))
        return {
            "policy_level": "operational",
            "routing_target": "operational_ticket",
            "confidence": round(confidence, 4),
            "strategic_score": strategic_score,
            "operational_score": operational_score,
            "reason": " ".join(reasons) or "Aspirasi lebih sesuai sebagai laporan teknis operasional.",
        }