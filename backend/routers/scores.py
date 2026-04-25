from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def getAllScores():

@router.get('/top')
async def getTopScores():

@router.get('/regional/{province}')
async def getScoresByProvince(province):

@router.get('/recompute')
async def recomputeScores():