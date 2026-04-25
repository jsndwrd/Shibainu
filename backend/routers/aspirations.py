from fastapi import APIRouter

router = APIRouter()

@router.post('/')
async def postAspiration():

@router.get('/')
async def getAllAspirations():

@router.get("/{aspiration_id}")
async def getAspirationById(aspiration_id):

@router.get("/{citizen_id}")
async def getAspirationsByCitizenId(citizen_id):