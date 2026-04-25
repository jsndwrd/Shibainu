from fastapi import APIRouter

router = APIRouter()

@router.get('/provinces')
async def getAllProvinces():

@router.get('/regencies/{province_id}')
async def getRegenciesByProvinceId(province_id):

@router.get('/categories')
async def getAllCategories():