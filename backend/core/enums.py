from enum import Enum


class CategoryEnum(str, Enum):
    INFRASTRUKTUR = "Infrastruktur"
    KESEHATAN = "Kesehatan"
    PENDIDIKAN = "Pendidikan"
    EKONOMI = "Ekonomi"
    LINGKUNGAN = "Lingkungan"
    KEAMANAN = "Keamanan"
    SOSIAL = "Sosial"


class ImpactScopeEnum(str, Enum):
    INDIVIDUAL = "Individual"
    COMMUNITY = "Community"
    REGIONAL = "Regional"
    NATIONAL = "National"


class TargetLevelEnum(str, Enum):
    REGENCY = "Regency"
    PROVINCIAL = "Provincial"
    NATIONAL = "National"


class SubmissionStatusEnum(str, Enum):
    RECEIVED = "received"
    PROCESSED = "processed"
    CLUSTERED = "clustered"
    SCORED = "scored"


class UrgencyClassEnum(str, Enum):
    SEGERA = "Segera"
    JANGKA_PENDEK = "Jangka Pendek"
    JANGKA_PANJANG = "Jangka Panjang"