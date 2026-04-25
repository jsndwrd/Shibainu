
class ReferenceService:
    def getProvinces(self):
        return ["Jawa Timur", "Jawa Barat"]

    def getRegencies(self, province: str):
        regProv = {
            "Jawa Timur": [
                "Surabaya",
                "Sidoarjo",
                "Malang",
            ],
            "DKI Jakarta": [
                "Jakarta Selatan",
                "Jakarta Barat",
            ],
        }

        return regProv.get(province, [])

    def getCategories(self):
        return [
            "Infrastruktur",
            "Kesehatan",
            "Pendidikan",
            "Ekonomi",
            "Lingkungan",
            "Keamanan",
            "Sosial",
        ]