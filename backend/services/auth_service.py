from datetime import date

from sqlalchemy.orm import Session

from core.security import create_access_token
from models import Citizen


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def loginByNIK(self, nik: str, dob: date):
        citizen = self.createDemoCitizens(nik, dob)

        if citizen.dob != dob:
            return None

        token = create_access_token({
            "sub": str(citizen.id),
            "role": "citizen",
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "citizen_id": citizen.id,
        }

    def getMe(self, citizen_id):
        return (
            self.db.query(Citizen)
            .filter(Citizen.id == citizen_id)
            .first()
        )

    def createDemoCitizens(self, nik: str, dob: date):
        citizen = (
            self.db.query(Citizen)
            .filter(Citizen.nik == nik)
            .first()
        )

        if citizen:
            return citizen

        citizen = Citizen(
            nik=nik,
            dob=dob,
        )

        self.db.add(citizen)
        self.db.commit()
        self.db.refresh(citizen)

        return citizen