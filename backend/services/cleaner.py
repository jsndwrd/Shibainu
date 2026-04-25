import re


class CleanerService:
    def __init__(self):
        self.slang_map = {
            "gak": "tidak",
            "ga": "tidak",
            "nggak": "tidak",
            "ngga": "tidak",
            "tdk": "tidak",
            "blm": "belum",
            "belom": "belum",
            "udh": "sudah",
            "sdh": "sudah",
            "bgt": "sangat",
            "banget": "sangat",
            "jln": "jalan",
            "jl": "jalan",
            "yg": "yang",
            "dgn": "dengan",
            "krn": "karena",
            "utk": "untuk",
            "rs": "rumah sakit",
            "rsud": "rumah sakit umum daerah",
            "puskes": "puskesmas",
            "pkm": "puskesmas",
            "bansos": "bantuan sosial",
        }

    def normalize_repeated_chars(self, text: str) -> str:
        return re.sub(r"(.)\1{2,}", r"\1\1", text)

    def cleanDesc(self, text: str) -> str:
        if not text:
            return ""

        text = str(text).strip()
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"http\S+|www\.\S+", " ", text)
        text = re.sub(r"@\w+", " ", text)

        text = text.lower()
        text = self.normalize_repeated_chars(text)
        text = re.sub(r"([!?.,]){2,}", r"\1", text)
        text = re.sub(r"[^a-zA-Z0-9À-ÿ\s.,!?/-]", " ", text)

        tokens = []
        for token in text.split():
            token = token.strip()
            token = self.slang_map.get(token, token)
            if token:
                tokens.append(token)

        text = " ".join(tokens)
        text = re.sub(r"\s+", " ", text).strip()

        return text