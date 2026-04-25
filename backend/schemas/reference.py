from pydantic import BaseModel

class ProvinceResponse(BaseModel):
    code: str
    name: str

class RegencyResponse(BaseModel):
    code: str
    name: str
    province_code: str