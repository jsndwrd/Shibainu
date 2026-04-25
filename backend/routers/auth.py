from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from services import AuthService
from schemas.auth import LoginRequest, LoginResponse, MeResponse

from core.database import get_db
from core.dependencies import get_current_user

router = APIRouter()

@router.post('/login', response_model=LoginResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    serv = AuthService(db)
    res = serv.loginByNIK(payload.nik, payload.dob)
    if not res:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials"
        )
    
    return res

# Delete frontend token locally.
@router.post('/logout')
async def logout(currUser=Depends(get_current_user)):
    return {"message": "Logged out successfully."}

@router.get('/me', response_model=MeResponse)
async def me(currUser=Depends(get_current_user), db: Session = Depends(get_db)):
    serv = AuthService(db)
    cz = serv.getMe(currUser)

    if not cz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User Not Found"
        )
    
    return cz