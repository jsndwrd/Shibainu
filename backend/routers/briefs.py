from fastapi import APIRouter

router = APIRouter()

@router.post('/generate')
async def generateBrief():

@router.get('/')
async def getAllBriefs():

@router.get('/{brief_id}')
async def getBriefById(brief_id):