from fastapi import APIRouter

router = APIRouter()

@router.get('/')
async def getAllClusters():

@router.get('/{cluster_id}')
async def getClusterById(cluster_id):

@router.post('/recompute')
async def recomputeClusters():