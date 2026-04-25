from fastapi import APIRouter

router = APIRouter()

@router.post('/login')
async def login():

@router.post('/logout')
async def logout():

@router.get('/me')
async def me():