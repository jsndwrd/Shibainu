from sqlalchemy.orm import Session
import random

class EmbedderService:
    def __init__(self, db: Session):
        self.db = db

    def predictCategory(self, text:str) -> str:
        text = text.lower()

        kMap = {
            "jalan": "Infrastruktur",
            "jembatan": "Infrastruktur",
            "rumah sakit": "Kesehatan",
            "puskesmas": "Kesehatan",
            "sekolah": "Pendidikan",
            "guru": "Pendidikan",
            "banjir": "Lingkungan",
            "sampah": "Lingkungan",
            "harga": "Ekonomi",
            "lapangan kerja": "Ekonomi",
        }

        for k, c in kMap.items():
            if k in text:
                return c
        
        return "Sosial"

    def predictUrgency(self, text:str) -> int:
        text = text.lower()
        if "darurat" in text or "segera" in text:
            return 5
        if "parah" in text:
            return 4
        if "tolong" in text:
            return 3

        return 2

    def generateEmbedding(self, text:str) -> list[float]:
        random.seed(hash(text) % 100000)
        return [round(random.random(), 6) for _ in range(768)]

    def predictAll(self, text:str) -> str:
        return {
            "category": self.predictCategory(text),
            "urgency": self.predictUrgency(text),
            "embedding": self.generateEmbedding(text),
        }
    