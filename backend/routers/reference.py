from fastapi import APIRouter

from schemas.reference import (
    ProvinceResponse,
    RegencyResponse,
)

from services.reference_service import ReferenceService

router = APIRouter()

@router.get('/provinces', response_model=list[ProvinceResponse])
async def getAllProvinces():
    serv = ReferenceService()
    data = serv.getProvinces()
    return [
        {"code": str(idx+1).zfill(2), "name": i} for idx, i in enumerate(data)
    ]

@router.get('/regencies/{province}', response_model=list[RegencyResponse])
async def getRegenciesByProvince(province: str):
    serv = ReferenceService()
    data = serv.getRegencies(province)

    return [
        { "code": f"{province[:2].upper()}{idx+1}", "name": i, "province_code": province[:2].upper()}
        for idx, i in enumerate(data)
    ]


@router.get('/categories')
async def getAllCategories():
    serv = ReferenceService()
    return serv.getCategories()