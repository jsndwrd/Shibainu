from __future__ import annotations

import random
import re
from collections import Counter
from datetime import date, datetime, timezone
from uuid import uuid4

from sqlalchemy import or_
from sqlalchemy.orm import Session

from models import Citizen, Aspiration, Cluster, ClusterScore


class DemoSeedService:
    ADMIN_NIK = "1111222233334444"
    ADMIN_DOB = date(1990, 1, 1)

    DEMO_NIK_PREFIX = "9900"
    GENERATED_BY = "Bulk Demo Seed"

    PROVINCE_REGENCIES = {
        "DKI Jakarta": [
            "Kota Administrasi Jakarta Selatan",
            "Kota Administrasi Jakarta Timur",
            "Kota Administrasi Jakarta Barat",
            "Kota Administrasi Jakarta Utara",
            "Kota Administrasi Jakarta Pusat",
        ],
        "Jawa Timur": [
            "Kota Surabaya",
            "Kabupaten Sidoarjo",
            "Kota Malang",
            "Kabupaten Gresik",
            "Kabupaten Jember",
        ],
        "Jawa Barat": [
            "Kota Bandung",
            "Kota Bekasi",
            "Kota Depok",
            "Kabupaten Bogor",
            "Kabupaten Bandung",
        ],
        "Jawa Tengah": [
            "Kota Semarang",
            "Kota Surakarta",
            "Kabupaten Banyumas",
            "Kabupaten Magelang",
            "Kabupaten Klaten",
        ],
        "Banten": [
            "Kota Tangerang",
            "Kota Tangerang Selatan",
            "Kabupaten Tangerang",
            "Kota Serang",
            "Kota Cilegon",
        ],
        "DI Yogyakarta": [
            "Kota Yogyakarta",
            "Kabupaten Sleman",
            "Kabupaten Bantul",
            "Kabupaten Gunungkidul",
            "Kabupaten Kulon Progo",
        ],
        "Bali": [
            "Kota Denpasar",
            "Kabupaten Badung",
            "Kabupaten Gianyar",
            "Kabupaten Tabanan",
            "Kabupaten Buleleng",
        ],
        "Sumatera Utara": [
            "Kota Medan",
            "Kota Binjai",
            "Kabupaten Deli Serdang",
            "Kabupaten Langkat",
            "Kota Pematangsiantar",
        ],
        "Sumatera Selatan": [
            "Kota Palembang",
            "Kota Prabumulih",
            "Kabupaten Banyuasin",
            "Kabupaten Ogan Ilir",
            "Kota Lubuklinggau",
        ],
        "Sulawesi Selatan": [
            "Kota Makassar",
            "Kota Parepare",
            "Kota Palopo",
            "Kabupaten Gowa",
            "Kabupaten Maros",
        ],
        "Kalimantan Timur": [
            "Kota Samarinda",
            "Kota Balikpapan",
            "Kota Bontang",
            "Kabupaten Kutai Kartanegara",
            "Kabupaten Penajam Paser Utara",
        ],
        "Papua": [
            "Kota Jayapura",
            "Kabupaten Jayapura",
            "Kabupaten Biak Numfor",
            "Kabupaten Sarmi",
            "Kabupaten Keerom",
        ],
    }

    CLUSTER_SPECS = [
        {
            "label": "Kerusakan Jalan dan Infrastruktur Dasar",
            "category": "Infrastruktur",
            "sub_topics": [
                "jalan rusak",
                "drainase buruk",
                "lampu jalan mati",
                "akses permukiman",
            ],
        },
        {
            "label": "Pelayanan Kesehatan Publik",
            "category": "Kesehatan",
            "sub_topics": [
                "antrean puskesmas",
                "ketersediaan obat",
                "akses lansia",
                "fasilitas kesehatan",
            ],
        },
        {
            "label": "Kualitas Pendidikan dan Fasilitas Sekolah",
            "category": "Pendidikan",
            "sub_topics": [
                "ruang kelas rusak",
                "akses internet sekolah",
                "beasiswa",
                "kekurangan guru",
            ],
        },
        {
            "label": "Pengelolaan Sampah dan Lingkungan",
            "category": "Lingkungan",
            "sub_topics": [
                "sampah menumpuk",
                "banjir",
                "pencemaran sungai",
                "ruang terbuka hijau",
            ],
        },
        {
            "label": "Transportasi Umum dan Kemacetan",
            "category": "Transportasi",
            "sub_topics": [
                "jadwal transportasi",
                "kemacetan",
                "halte rusak",
                "integrasi moda",
            ],
        },
        {
            "label": "Keamanan Lingkungan Warga",
            "category": "Keamanan",
            "sub_topics": [
                "penerangan minim",
                "rawan pencurian",
                "patroli lingkungan",
                "kamera pengawas",
            ],
        },
        {
            "label": "Bantuan Sosial dan Ketepatan Sasaran",
            "category": "Sosial",
            "sub_topics": [
                "bansos tidak tepat sasaran",
                "validasi data warga",
                "kelompok rentan",
                "layanan sosial",
            ],
        },
        {
            "label": "UMKM dan Pemulihan Ekonomi Lokal",
            "category": "Ekonomi",
            "sub_topics": [
                "akses modal",
                "pelatihan UMKM",
                "pasar tradisional",
                "digitalisasi usaha",
            ],
        },
        {
            "label": "Pelayanan Administrasi Publik",
            "category": "Pelayanan Publik",
            "sub_topics": [
                "antrean layanan",
                "dokumen kependudukan",
                "respons petugas",
                "prosedur layanan",
            ],
        },
        {
            "label": "Layanan Digital Pemerintah",
            "category": "Digitalisasi",
            "sub_topics": [
                "aplikasi error",
                "server lambat",
                "akses layanan online",
                "integrasi data",
            ],
        },
    ]

    DESCRIPTION_TEMPLATES = {
        "Infrastruktur": [
            "Jalan utama di {regency}, {province} rusak parah dan membahayakan pengendara setiap hari.",
            "Drainase di {regency}, {province} sering tersumbat sehingga air meluap saat hujan deras.",
            "Lampu jalan di kawasan permukiman {regency}, {province} mati selama beberapa minggu.",
            "Akses warga menuju fasilitas publik di {regency}, {province} terganggu karena kondisi jalan berlubang.",
        ],
        "Kesehatan": [
            "Antrean layanan kesehatan di {regency}, {province} terlalu panjang dan menyulitkan warga lansia.",
            "Ketersediaan obat dasar di fasilitas kesehatan {regency}, {province} sering kosong.",
            "Warga di {regency}, {province} membutuhkan akses layanan kesehatan yang lebih cepat dan jelas.",
            "Pelayanan kesehatan ibu dan anak di {regency}, {province} perlu ditingkatkan karena antrean sangat padat.",
        ],
        "Pendidikan": [
            "Ruang kelas di {regency}, {province} mengalami kerusakan dan mengganggu kegiatan belajar siswa.",
            "Sekolah di {regency}, {province} membutuhkan akses internet yang stabil untuk pembelajaran digital.",
            "Warga di {regency}, {province} meminta pemerataan bantuan pendidikan bagi siswa kurang mampu.",
            "Beberapa sekolah di {regency}, {province} kekurangan tenaga pengajar pada mata pelajaran utama.",
        ],
        "Lingkungan": [
            "Sampah menumpuk di area publik {regency}, {province} dan menimbulkan bau tidak sedap.",
            "Banjir berulang terjadi di {regency}, {province} karena saluran air tidak berfungsi baik.",
            "Sungai di {regency}, {province} tercemar limbah dan perlu penanganan dari dinas terkait.",
            "Warga {regency}, {province} membutuhkan ruang terbuka hijau yang lebih layak.",
        ],
        "Transportasi": [
            "Transportasi umum di {regency}, {province} tidak konsisten sehingga warga sering terlambat bekerja.",
            "Kemacetan di titik utama {regency}, {province} semakin parah pada jam berangkat kerja.",
            "Halte transportasi di {regency}, {province} rusak dan tidak nyaman digunakan warga.",
            "Integrasi transportasi umum di {regency}, {province} perlu diperbaiki agar perjalanan lebih efisien.",
        ],
        "Keamanan": [
            "Penerangan jalan di {regency}, {province} kurang memadai dan membuat warga merasa tidak aman.",
            "Beberapa titik di {regency}, {province} rawan pencurian dan membutuhkan patroli rutin.",
            "Warga {regency}, {province} meminta pemasangan kamera pengawas di area rawan.",
            "Lingkungan permukiman di {regency}, {province} membutuhkan peningkatan sistem keamanan warga.",
        ],
        "Sosial": [
            "Penyaluran bantuan sosial di {regency}, {province} belum tepat sasaran menurut warga setempat.",
            "Data penerima bantuan di {regency}, {province} perlu diperbarui agar kelompok rentan terlayani.",
            "Warga kurang mampu di {regency}, {province} membutuhkan akses layanan sosial yang lebih jelas.",
            "Distribusi bantuan di {regency}, {province} perlu dipantau agar tidak terjadi tumpang tindih data.",
        ],
        "Ekonomi": [
            "Pelaku UMKM di {regency}, {province} membutuhkan akses modal dan pendampingan usaha.",
            "Pedagang pasar di {regency}, {province} meminta perbaikan fasilitas dan kebersihan pasar.",
            "Warga {regency}, {province} membutuhkan pelatihan digital untuk memperluas pemasaran produk lokal.",
            "Pemulihan ekonomi lokal di {regency}, {province} perlu didukung dengan program usaha produktif.",
        ],
        "Pelayanan Publik": [
            "Antrean administrasi publik di {regency}, {province} terlalu panjang dan perlu sistem layanan lebih cepat.",
            "Pengurusan dokumen kependudukan di {regency}, {province} masih membingungkan sebagian warga.",
            "Respons petugas layanan publik di {regency}, {province} perlu ditingkatkan agar lebih informatif.",
            "Prosedur pelayanan di {regency}, {province} perlu dibuat lebih sederhana dan transparan.",
        ],
        "Digitalisasi": [
            "Aplikasi layanan pemerintah di {regency}, {province} sering error saat digunakan warga.",
            "Server layanan digital di {regency}, {province} lambat dan menghambat proses administrasi.",
            "Warga {regency}, {province} kesulitan mengakses layanan online karena sistem tidak stabil.",
            "Integrasi data layanan digital di {regency}, {province} perlu diperbaiki agar tidak berulang input.",
        ],
    }

    STATUS_POOL = [
        "submitted",
        "submitted",
        "submitted",
        "in_review",
        "in_review",
        "resolved",
        "rejected",
    ]

    URGENCY_WEIGHTS = [8, 17, 35, 25, 15]

    def __init__(self, db: Session):
        self.db = db
        self.random = random.Random(42)

    def seedDemoData(self, total_aspirations: int = 120):
        total_aspirations = max(80, min(total_aspirations, 300))

        admin = self._getOrCreateCitizen(
            nik=self.ADMIN_NIK,
            dob=self.ADMIN_DOB,
            province="DKI Jakarta",
            regency="Kota Administrasi Jakarta Selatan",
            role="admin",
        )

        citizens = self._seedCitizens(
            total_citizens=max(total_aspirations, 100)
        )

        clusters = self._seedClusters()

        aspirations = self._seedAspirations(
            citizens=citizens,
            clusters=clusters,
            total_aspirations=total_aspirations,
        )

        self._recalculateClusters()

        scores = self._seedScores()
        briefs = self._seedBriefs()

        self.db.commit()

        return {
            "message": "Bulk demo data seeded successfully.",
            "accounts": {
                "admin": {
                    "nik": self.ADMIN_NIK,
                    "dob": self.ADMIN_DOB.isoformat(),
                    "role": "admin",
                },
                "sample_user": {
                    "nik": citizens[0].nik,
                    "dob": citizens[0].dob.isoformat(),
                    "role": "user",
                },
            },
            "created_or_updated": {
                "admin": 1 if admin else 0,
                "citizens": len(citizens),
                "clusters": len(clusters),
                "aspirations": len(aspirations),
                "scores": len(scores),
                "briefs": len(briefs),
            },
            "dashboard_ready": True,
        }

    def resetDemoData(self):
        demo_citizens = (
            self.db.query(Citizen)
            .filter(
                or_(
                    Citizen.nik.like(f"{self.DEMO_NIK_PREFIX}%"),
                    Citizen.nik == self.ADMIN_NIK,
                )
            )
            .all()
        )

        demo_citizen_ids = [citizen.id for citizen in demo_citizens]

        demo_cluster_labels = [
            cluster["label"] for cluster in self.CLUSTER_SPECS
        ]

        demo_clusters = (
            self.db.query(Cluster)
            .filter(Cluster.label.in_(demo_cluster_labels))
            .all()
        )

        demo_cluster_ids = [cluster.id for cluster in demo_clusters]

        PolicyBrief = self._getPolicyBriefModelOrNone()

        if PolicyBrief is not None and demo_cluster_ids:
            (
                self.db.query(PolicyBrief)
                .filter(PolicyBrief.cluster_id.in_(demo_cluster_ids))
                .delete(synchronize_session=False)
            )

        if demo_cluster_ids:
            (
                self.db.query(ClusterScore)
                .filter(ClusterScore.cluster_id.in_(demo_cluster_ids))
                .delete(synchronize_session=False)
            )

            if hasattr(Aspiration, "cluster_id"):
                (
                    self.db.query(Aspiration)
                    .filter(Aspiration.cluster_id.in_(demo_cluster_ids))
                    .delete(synchronize_session=False)
                )

        if demo_citizen_ids:
            (
                self.db.query(Aspiration)
                .filter(Aspiration.citizen_id.in_(demo_citizen_ids))
                .delete(synchronize_session=False)
            )

        for cluster in demo_clusters:
            self.db.delete(cluster)

        for citizen in demo_citizens:
            self.db.delete(citizen)

        self.db.commit()

        return {
            "message": "Bulk demo data reset successfully.",
        }

    def getStats(self):
        PolicyBrief = self._getPolicyBriefModelOrNone()

        total_briefs = 0

        if PolicyBrief is not None:
            total_briefs = self.db.query(PolicyBrief).count()

        return {
            "total_citizens": self.db.query(Citizen).count(),
            "total_aspirations": self.db.query(Aspiration).count(),
            "total_clusters": self.db.query(Cluster).count(),
            "total_scores": self.db.query(ClusterScore).count(),
            "total_briefs": total_briefs,
        }

    def _seedCitizens(self, total_citizens: int):
        citizens = []
        province_names = list(self.PROVINCE_REGENCIES.keys())

        for idx in range(1, total_citizens + 1):
            province = self.random.choice(province_names)
            regency = self.random.choice(self.PROVINCE_REGENCIES[province])

            nik = f"{self.DEMO_NIK_PREFIX}{idx:012d}"

            year = self.random.randint(1970, 2005)
            month = self.random.randint(1, 12)
            day = self.random.randint(1, 28)

            citizen = self._getOrCreateCitizen(
                nik=nik,
                dob=date(year, month, day),
                province=province,
                regency=regency,
                role="user",
            )

            citizens.append(citizen)

        return citizens

    def _seedClusters(self):
        clusters = []

        for spec in self.CLUSTER_SPECS:
            cluster = self._getOrCreateCluster(
                label=spec["label"],
                category=spec["category"],
                member_count=0,
                avg_urgency=0.0,
                top_provinces=[],
                priority_score=0.0,
                population=0,
                dominant_asta_cita=self._categoryToAstaCita(spec["category"]),
                asta_confidence=0.84,
                sub_topics=spec["sub_topics"],
                urgency_dist={
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0,
                },
            )

            clusters.append(cluster)

        return clusters

    def _seedAspirations(
        self,
        citizens,
        clusters,
        total_aspirations: int,
    ):
        aspirations = []

        for idx in range(1, total_aspirations + 1):
            citizen = self.random.choice(citizens)
            cluster = self.random.choice(clusters)

            urgency = self.random.choices(
                population=[1, 2, 3, 4, 5],
                weights=self.URGENCY_WEIGHTS,
                k=1,
            )[0]

            status = self.random.choice(self.STATUS_POOL)

            category = getattr(cluster, "category", "Pelayanan Publik")

            description = self._buildDescription(
                category=category,
                province=getattr(citizen, "province", "Indonesia"),
                regency=getattr(citizen, "regency", "Wilayah"),
                idx=idx,
            )

            priority_score = self._calculateAspirationPriority(
                urgency=urgency,
                status=status,
            )

            aspiration = self._getOrCreateAspiration(
                citizen_id=citizen.id,
                cluster_id=cluster.id,
                description=description,
                cleaned_description=self._cleanText(description),
                predicted_category=category,
                predicted_urgency=urgency,
                priority_score=priority_score,
                status=status,
            )

            aspirations.append(aspiration)

        return aspirations

    def _seedScores(self):
        scores = []

        demo_cluster_labels = [
            cluster["label"] for cluster in self.CLUSTER_SPECS
        ]

        clusters = (
            self.db.query(Cluster)
            .filter(Cluster.label.in_(demo_cluster_labels))
            .all()
        )

        for cluster in clusters:
            member_count = float(getattr(cluster, "member_count", 0) or 0)
            avg_urgency = float(getattr(cluster, "avg_urgency", 0) or 0)
            top_provinces = getattr(cluster, "top_provinces", []) or []

            volume_score = min(100.0, member_count * 7.5)
            urgency_score = min(100.0, avg_urgency * 20.0)
            geo_score = min(100.0, len(top_provinces) * 20.0)

            impact_score = min(
                100.0,
                volume_score * 0.25
                + urgency_score * 0.45
                + geo_score * 0.30,
            )

            total_score = round(
                volume_score * 0.25
                + urgency_score * 0.35
                + geo_score * 0.20
                + impact_score * 0.20,
                2,
            )

            score = self._getOrCreateScore(
                cluster_id=cluster.id,
                volume_score=round(volume_score, 2),
                urgency_score=round(urgency_score, 2),
                geo_score=round(geo_score, 2),
                impact_score=round(impact_score, 2),
                total_score=total_score,
            )

            self._setIfExists(cluster, "priority_score", total_score)
            self._setIfExists(
                cluster,
                "last_updated",
                datetime.now(timezone.utc),
            )

            scores.append(score)

        return scores

    def _seedBriefs(self):
        PolicyBrief = self._getPolicyBriefModelOrNone()

        if PolicyBrief is None:
            return []

        demo_cluster_labels = [
            cluster["label"] for cluster in self.CLUSTER_SPECS
        ]

        clusters = (
            self.db.query(Cluster)
            .filter(Cluster.label.in_(demo_cluster_labels))
            .order_by(Cluster.priority_score.desc())
            .limit(5)
            .all()
        )

        briefs = []

        for cluster in clusters:
            urgency_classification = self._classifyUrgency(
                getattr(cluster, "priority_score", 0)
            )

            sub_topics = getattr(cluster, "sub_topics", []) or []
            top_provinces = getattr(cluster, "top_provinces", []) or []

            content = (
                f"Cluster '{cluster.label}' menunjukkan prioritas "
                f"{urgency_classification.lower()} dengan skor "
                f"{round(float(getattr(cluster, 'priority_score', 0) or 0), 2)}. "
                f"Isu utama mencakup {', '.join(sub_topics)}. "
                f"Data berasal dari {getattr(cluster, 'member_count', 0)} aspirasi warga "
                f"dengan rata-rata urgensi {round(float(getattr(cluster, 'avg_urgency', 0) or 0), 2)}. "
                f"Wilayah paling sering muncul adalah "
                f"{', '.join(top_provinces or ['belum tersedia'])}. "
                f"Rekomendasi awal adalah melakukan verifikasi lapangan, "
                f"menentukan instansi penanggung jawab, dan menyusun tindak lanjut "
                f"berdasarkan tingkat prioritas wilayah."
            )

            brief = self._getOrCreateBrief(
                cluster_id=cluster.id,
                content=content,
                urgency_classification=urgency_classification,
                generated_by=self.GENERATED_BY,
            )

            if brief is not None:
                briefs.append(brief)

        return briefs

    def _recalculateClusters(self):
        demo_cluster_labels = [
            cluster["label"] for cluster in self.CLUSTER_SPECS
        ]

        clusters = (
            self.db.query(Cluster)
            .filter(Cluster.label.in_(demo_cluster_labels))
            .all()
        )

        for cluster in clusters:
            if not hasattr(Aspiration, "cluster_id"):
                continue

            aspirations = (
                self.db.query(Aspiration)
                .filter(Aspiration.cluster_id == cluster.id)
                .all()
            )

            if not aspirations:
                self._setIfExists(cluster, "member_count", 0)
                self._setIfExists(cluster, "avg_urgency", 0.0)
                self._setIfExists(cluster, "top_provinces", [])
                self._setIfExists(cluster, "priority_score", 0.0)
                self._setIfExists(cluster, "population", 0)
                self._setIfExists(
                    cluster,
                    "dominant_asta_cita",
                    self._categoryToAstaCita(
                        getattr(cluster, "category", "")
                    ),
                )
                self._setIfExists(cluster, "asta_confidence", 0.84)
                self._setIfExists(
                    cluster,
                    "urgency_dist",
                    {
                        "1": 0,
                        "2": 0,
                        "3": 0,
                        "4": 0,
                        "5": 0,
                    },
                )
                self._setIfExists(
                    cluster,
                    "last_updated",
                    datetime.now(timezone.utc),
                )

                continue

            urgency_values = [
                self._getAspirationUrgency(aspiration)
                for aspiration in aspirations
            ]

            urgency_counter = Counter(urgency_values)
            citizen_ids = [aspiration.citizen_id for aspiration in aspirations]

            citizens = (
                self.db.query(Citizen)
                .filter(Citizen.id.in_(citizen_ids))
                .all()
            )

            province_counter = Counter(
                citizen.province
                for citizen in citizens
                if getattr(citizen, "province", None)
            )

            top_provinces = [
                province
                for province, _ in province_counter.most_common(3)
            ]

            member_count = len(aspirations)
            avg_urgency = round(
                sum(urgency_values) / len(urgency_values),
                2,
            )

            urgency_dist = {
                str(level): urgency_counter.get(level, 0)
                for level in range(1, 6)
            }

            priority_score = self._calculateClusterPriority(
                member_count=member_count,
                avg_urgency=avg_urgency,
                province_count=len(top_provinces),
            )

            population = member_count * 1200
            dominant_asta_cita = self._categoryToAstaCita(
                getattr(cluster, "category", "")
            )

            self._setIfExists(cluster, "member_count", member_count)
            self._setIfExists(cluster, "avg_urgency", avg_urgency)
            self._setIfExists(cluster, "top_provinces", top_provinces)
            self._setIfExists(cluster, "urgency_dist", urgency_dist)
            self._setIfExists(cluster, "priority_score", priority_score)
            self._setIfExists(cluster, "population", population)
            self._setIfExists(cluster, "dominant_asta_cita", dominant_asta_cita)
            self._setIfExists(cluster, "asta_confidence", 0.84)
            self._setIfExists(
                cluster,
                "last_updated",
                datetime.now(timezone.utc),
            )

    def _getOrCreateCitizen(
        self,
        nik: str,
        dob: date,
        province: str,
        regency: str,
        role: str,
    ):
        citizen = self.db.query(Citizen).filter(Citizen.nik == nik).first()

        if not citizen:
            citizen = Citizen()
            self.db.add(citizen)

        self._setIfExists(citizen, "id", getattr(citizen, "id", None) or uuid4())
        self._setIfExists(citizen, "nik", nik)
        self._setIfExists(citizen, "dob", dob)
        self._setIfExists(citizen, "province", province)
        self._setIfExists(citizen, "regency", regency)
        self._setIfExists(citizen, "role", role)

        self.db.flush()

        return citizen

    def _getOrCreateCluster(
        self,
        label: str,
        category: str,
        member_count: int,
        avg_urgency: float,
        top_provinces: list[str],
        priority_score: float,
        population: int,
        dominant_asta_cita: str,
        asta_confidence: float,
        sub_topics: list[str],
        urgency_dist: dict,
    ):
        cluster = self.db.query(Cluster).filter(Cluster.label == label).first()

        if not cluster:
            cluster = Cluster()
            self.db.add(cluster)

        self._setIfExists(cluster, "id", getattr(cluster, "id", None) or uuid4())
        self._setIfExists(cluster, "label", label)
        self._setIfExists(cluster, "category", category)
        self._setIfExists(cluster, "member_count", member_count)
        self._setIfExists(cluster, "avg_urgency", avg_urgency)
        self._setIfExists(cluster, "top_provinces", top_provinces)
        self._setIfExists(cluster, "priority_score", priority_score)
        self._setIfExists(cluster, "population", population)
        self._setIfExists(cluster, "dominant_asta_cita", dominant_asta_cita)
        self._setIfExists(cluster, "asta_confidence", asta_confidence)
        self._setIfExists(cluster, "sub_topics", sub_topics)
        self._setIfExists(cluster, "urgency_dist", urgency_dist)
        self._setIfExists(
            cluster,
            "created_at",
            getattr(cluster, "created_at", None) or datetime.now(timezone.utc),
        )
        self._setIfExists(
            cluster,
            "last_updated",
            datetime.now(timezone.utc),
        )

        self.db.flush()

        return cluster

    def _getOrCreateAspiration(
        self,
        citizen_id,
        cluster_id,
        description: str,
        cleaned_description: str,
        predicted_category: str,
        predicted_urgency: int,
        priority_score: float,
        status: str,
    ):
        aspiration = (
            self.db.query(Aspiration)
            .filter(Aspiration.description == description)
            .first()
        )

        if not aspiration:
            aspiration = Aspiration()
            self.db.add(aspiration)

        self._setIfExists(
            aspiration,
            "id",
            getattr(aspiration, "id", None) or uuid4(),
        )
        self._setIfExists(aspiration, "citizen_id", citizen_id)
        self._setIfExists(aspiration, "description", description)
        self._setIfExists(aspiration, "cleaned_description", cleaned_description)

        self._setIfExists(aspiration, "category_user_input", predicted_category)
        self._setIfExists(aspiration, "category", predicted_category)
        self._setIfExists(aspiration, "predicted_category", predicted_category)
        self._setIfExists(aspiration, "category_confidence", 0.86)

        self._setIfExists(aspiration, "urgency", predicted_urgency)
        self._setIfExists(aspiration, "predicted_urgency", predicted_urgency)
        self._setIfExists(aspiration, "priority_score", priority_score)

        self._setIfExists(aspiration, "predicted_asta_cita", "Asta Cita 6")
        self._setIfExists(aspiration, "asta_confidence", 0.82)

        self._setIfExists(
            aspiration,
            "policy_level",
            self._urgencyToPolicyLevel(predicted_urgency),
        )
        self._setIfExists(aspiration, "policy_level_confidence", 0.8)
        self._setIfExists(
            aspiration,
            "policy_level_reason",
            "Generated from demo seed urgency level.",
        )

        self._setIfExists(aspiration, "routing_target", "Pemerintah Daerah")
        self._setIfExists(
            aspiration,
            "province",
            self._getCitizenProvince(citizen_id),
        )
        self._setIfExists(
            aspiration,
            "regency",
            self._getCitizenRegency(citizen_id),
        )
        self._setIfExists(aspiration, "impact_scope", "local")
        self._setIfExists(aspiration, "target_level", "daerah")
        self._setIfExists(aspiration, "cluster_id", cluster_id)
        self._setIfExists(aspiration, "status", status)
        self._setIfExists(
            aspiration,
            "submitted_at",
            getattr(aspiration, "submitted_at", None)
            or datetime.now(timezone.utc),
        )

        self.db.flush()

        return aspiration

    def _getOrCreateScore(
        self,
        cluster_id,
        volume_score: float,
        urgency_score: float,
        geo_score: float,
        impact_score: float,
        total_score: float,
    ):
        score = None

        if hasattr(ClusterScore, "cluster_id"):
            score = (
                self.db.query(ClusterScore)
                .filter(ClusterScore.cluster_id == cluster_id)
                .first()
            )

        if not score:
            score = ClusterScore()
            self.db.add(score)

        self._setIfExists(score, "id", getattr(score, "id", None) or uuid4())
        self._setIfExists(score, "cluster_id", cluster_id)
        self._setIfExists(score, "volume_score", volume_score)
        self._setIfExists(score, "urgency_score", urgency_score)
        self._setIfExists(score, "geo_score", geo_score)
        self._setIfExists(score, "impact_score", impact_score)
        self._setIfExists(score, "total_score", total_score)
        self._setIfExists(score, "computed_at", datetime.now(timezone.utc))

        self.db.flush()

        return score

    def _getOrCreateBrief(
        self,
        cluster_id,
        content: str,
        urgency_classification: str,
        generated_by: str,
    ):
        PolicyBrief = self._getPolicyBriefModelOrNone()

        if PolicyBrief is None:
            return None

        brief = None

        if hasattr(PolicyBrief, "cluster_id") and hasattr(
            PolicyBrief,
            "generated_by",
        ):
            brief = (
                self.db.query(PolicyBrief)
                .filter(
                    PolicyBrief.cluster_id == cluster_id,
                    PolicyBrief.generated_by == generated_by,
                )
                .first()
            )

        if not brief:
            brief = PolicyBrief()
            self.db.add(brief)

        self._setIfExists(brief, "id", getattr(brief, "id", None) or uuid4())
        self._setIfExists(brief, "cluster_id", cluster_id)
        self._setIfExists(brief, "content", content)
        self._setIfExists(
            brief,
            "urgency_classification",
            urgency_classification,
        )
        self._setIfExists(brief, "generated_by", generated_by)
        self._setIfExists(brief, "generated_at", datetime.now(timezone.utc))

        self.db.flush()

        return brief

    def _setIfExists(self, model, field: str, value):
        if hasattr(model, field):
            setattr(model, field, value)

    def _getPolicyBriefModelOrNone(self):
        try:
            return self.db.registry.mapped["PolicyBrief"]
        except Exception:
            return None

    def _buildDescription(
        self,
        category: str,
        province: str,
        regency: str,
        idx: int,
    ) -> str:
        templates = self.DESCRIPTION_TEMPLATES.get(
            category,
            self.DESCRIPTION_TEMPLATES["Pelayanan Publik"],
        )

        template = self.random.choice(templates)

        return (
            template.format(
                province=province,
                regency=regency,
            )
            + f" Laporan demo nomor {idx} dibuat untuk kebutuhan pengujian statistik dashboard."
        )

    def _cleanText(self, text: str) -> str:
        lowered = text.lower()
        cleaned = re.sub(r"[^a-z0-9\s]", " ", lowered)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()

        return cleaned

    def _calculateAspirationPriority(
        self,
        urgency: int,
        status: str,
    ) -> float:
        status_weight = {
            "submitted": 12,
            "in_review": 8,
            "resolved": 3,
            "rejected": 1,
        }.get(status, 5)

        random_weight = self.random.uniform(5, 20)

        return round(
            min(100.0, urgency * 15 + status_weight + random_weight),
            2,
        )

    def _calculateClusterPriority(
        self,
        member_count: int,
        avg_urgency: float,
        province_count: int,
    ) -> float:
        volume_score = min(100.0, member_count * 7.5)
        urgency_score = min(100.0, avg_urgency * 20.0)
        geo_score = min(100.0, province_count * 20.0)

        return round(
            volume_score * 0.35
            + urgency_score * 0.45
            + geo_score * 0.20,
            2,
        )

    def _classifyUrgency(self, priority_score: float) -> str:
        score = float(priority_score or 0)

        if score >= 85:
            return "Kritis"

        if score >= 70:
            return "Tinggi"

        if score >= 50:
            return "Sedang"

        return "Rendah"

    def _urgencyToPolicyLevel(self, urgency: int) -> str:
        if urgency >= 5:
            return "nasional"

        if urgency >= 4:
            return "provinsi"

        return "daerah"

    def _categoryToAstaCita(self, category: str) -> str:
        mapping = {
            "Infrastruktur": "Asta Cita 6",
            "Kesehatan": "Asta Cita 4",
            "Pendidikan": "Asta Cita 4",
            "Lingkungan": "Asta Cita 8",
            "Transportasi": "Asta Cita 6",
            "Keamanan": "Asta Cita 1",
            "Sosial": "Asta Cita 4",
            "Ekonomi": "Asta Cita 3",
            "Pelayanan Publik": "Asta Cita 7",
            "Digitalisasi": "Asta Cita 7",
        }

        return mapping.get(category, "Asta Cita 7")

    def _getCitizenProvince(self, citizen_id):
        citizen = (
            self.db.query(Citizen)
            .filter(Citizen.id == citizen_id)
            .first()
        )

        if not citizen:
            return None

        return getattr(citizen, "province", None)

    def _getCitizenRegency(self, citizen_id):
        citizen = (
            self.db.query(Citizen)
            .filter(Citizen.id == citizen_id)
            .first()
        )

        if not citizen:
            return None

        return getattr(citizen, "regency", None)

    def _getAspirationUrgency(self, aspiration) -> int:
        predicted_urgency = getattr(aspiration, "predicted_urgency", None)

        if predicted_urgency:
            return int(predicted_urgency)

        urgency = getattr(aspiration, "urgency", None)

        if urgency:
            return int(urgency)

        policy_level = getattr(aspiration, "policy_level", None)

        policy_level_map = {
            "daerah": 3,
            "provinsi": 4,
            "nasional": 5,
            "local": 3,
            "regional": 4,
            "national": 5,
        }

        return policy_level_map.get(str(policy_level).lower(), 3)