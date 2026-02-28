from fastapi import APIRouter, HTTPException, Depends
from app.api.services.auth_service import AuthService
from app.api.models.user import UserSignup, UserLogin

router = APIRouter()

def get_auth_service():
    return AuthService()


@router.post("/signup")
def signup(user: UserSignup, auth_service: AuthService = Depends(get_auth_service)):
    result = auth_service.signup(user)
    if not result:
        raise HTTPException(status_code=400, detail="User already exists")
    return result


@router.post("/login")
def login(user: UserLogin, auth_service: AuthService = Depends(get_auth_service)):
    result = auth_service.login(user)
    if not result:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return result



