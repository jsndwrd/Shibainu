import hashlib
import random
from typing import Dict, List


class EmbedderService:
    def __init__(self, db=None):
        self.db = db

    def predict_category(self, text: str) -> str:
        text = (text or "").lower()

        keyword_map = {
            "Infrastruktur": [
                "jalan", "jembatan", "drainase", "lampu jalan", "trotoar",
                "aspal", "berlubang", "irigasi", "akses desa",
            ],
            "Kesehatan": [
                "rumah sakit", "puskesmas", "dokter", "obat", "bpjs",
                "ambulans", "pasien", "posyandu", "stunting",
            ],
            "Pendidikan": [
                "sekolah", "guru", "siswa", "murid", "kelas", "kampus",
                "kuliah", "buku", "beasiswa",
            ],
            "Lingkungan": [
                "banjir", "sampah", "limbah", "polusi", "pencemaran",
                "sungai", "asap", "hutan",
            ],
            "Ekonomi": [
                "harga", "sembako", "beras", "pasar", "umkm",
                "pengangguran", "lapangan kerja", "pupuk", "bbm",
            ],
            "Keamanan": [
                "begal", "maling", "pencurian", "tawuran", "narkoba",
                "preman", "kriminal", "polisi",
            ],
            "Sosial": [
                "bansos", "bantuan sosial", "pkh", "blt", "lansia",
                "disabilitas", "miskin", "kelaparan",
            ],
        }

        scores = {}

        for category, keywords in keyword_map.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            scores[category] = score

        best_category = max(scores, key=scores.get)

        if scores[best_category] == 0:
            return "Sosial"

        return best_category

    def predict_asta_cita(self, text: str, category: str) -> Dict:
        text = (text or "").lower()

        if category == "Kesehatan":
            return {"asta_cita": "Misi 4", "confidence": 0.86}

        if category == "Pendidikan":
            return {"asta_cita": "Misi 4", "confidence": 0.86}

        if category == "Infrastruktur":
            if "desa" in text or "kelurahan" in text:
                return {"asta_cita": "Misi 6", "confidence": 0.84}
            return {"asta_cita": "Misi 3", "confidence": 0.82}

        if category == "Ekonomi":
            if any(k in text for k in ["pangan", "beras", "pupuk", "petani", "nelayan"]):
                return {"asta_cita": "Misi 2", "confidence": 0.84}
            if any(k in text for k in ["industri", "pabrik", "hilirisasi"]):
                return {"asta_cita": "Misi 5", "confidence": 0.80}
            return {"asta_cita": "Misi 3", "confidence": 0.78}

        if category == "Lingkungan":
            return {"asta_cita": "Misi 8", "confidence": 0.82}

        if category == "Keamanan":
            if "narkoba" in text or "korupsi" in text:
                return {"asta_cita": "Misi 7", "confidence": 0.82}
            return {"asta_cita": "Misi 1", "confidence": 0.80}

        if category == "Sosial":
            if any(k in text for k in ["desa", "kelurahan", "bansos", "pkh", "blt"]):
                return {"asta_cita": "Misi 6", "confidence": 0.78}
            return {"asta_cita": "Misi 1", "confidence": 0.76}

        return {"asta_cita": "Misi UNKNOWN", "confidence": 0.30}

    def generate_embedding(self, text: str) -> List[float]:
        """
        Fallback embedding deterministic.
        Nanti bisa diganti embedding dari IndoBERT saat .bin sudah tersedia.
        """
        seed = int(hashlib.md5((text or "").encode("utf-8")).hexdigest(), 16) % 100000
        random.seed(seed)
        return [round(random.random(), 6) for _ in range(768)]

    def predict_all(self, text: str) -> Dict:
        category = self.predict_category(text)
        asta = self.predict_asta_cita(text=text, category=category)
        embedding = self.generate_embedding(text)

        return {
            "category": category,
            "asta_cita": asta["asta_cita"],
            "asta_confidence": asta["confidence"],
            "embedding": embedding,
        }

    # Compatibility alias untuk kode lama
    def predictAll(self, text: str) -> Dict:
        return self.predict_all(text)