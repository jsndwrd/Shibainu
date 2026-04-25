from sqlalchemy.orm import Session
from models import Citizen
from datetime import date

from core.security import create_access_token

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def loginByNIK(self, nik: str, dob: date):
        cz = self.createDemoCitizens(nik, dob)

        if cz.dob != dob:
            return None
        
        token = create_access_token({
            "sub": str(cz.id),
            "role": "citizen"
        })

        return {
            "access_token": token,
            "token_type": "bearer",
            "citizen_id": cz.id
        }

        
    def getMe(self, citizen_id):
        return (self.db.query(Citizen).filter(Citizen.id == citizen_id).first())

    def createDemoCitizens(self, nik:str, dob: date):
        cz = (self.db.query(Citizen).filter(Citizen.nik == nik).first())

        if cz:
            return cz
        
        cz = Citizen(nik=nik, dob=dob)

        self.db.add(cz)
        self.db.commit()
        self.db.refersh(cz)

        return cz



    