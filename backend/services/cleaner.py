import re
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

class CleanerService:
    def normalizeSlang(self, text: str) -> str:
        slangMap = {
            "gak": "tidak", "ga": "tidak", "nggak": "tidak",
            "gw": "saya", "gue": "saya", "aku": "saya",
            "bgt": "sangat", "bngt": "sangat", "banget": "sangat",
            "blm": "belum", "udh": "sudah", "sdh": "sudah",
            "jln": "jalan", "jl": "jalan", "jlnan": "jalanan",
            "rs": "rumah sakit", "rsud": "rumah sakit umum daerah",
            "pskms": "puskesmas", "pkm": "puskesmas",
            "sy": "saya", "krn": "karena", "yg": "yang",
            "dgn": "dengan", "utk": "untuk", "kpd": "kepada",
            "tdk": "tidak", "sdg": "sedang", "msh": "masih",
            "thn": "tahun", "bln": "bulan", "hr": "hari",
        }

        ws = text.split()
        ws = [slangMap.get(w.lower(), w) for w in ws]
        return " ".join(ws)

    def stripNoise(self, text: str) -> str:
        text = re.sub(r"http\S+", "", text)
        text = re.sub(r"[^a-zA-Z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def stemText(self, text: str) -> str:
        factory = StemmerFactory()
        stemmer = factory.create_stemmer()
        return stemmer.stem(text)

    def cleanDesc(self, text: str) -> str:
        text = self.normalizeSlang(text)
        text = self.stripNoise(text)
        text = self.stemText(text)
        return text.lower()
