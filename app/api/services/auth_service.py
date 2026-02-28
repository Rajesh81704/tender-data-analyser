from app.api.dao.user_dao import UserDAO
from app.api.models.user import UserSignup, UserLogin
from app.api.utils.jwt_handler import create_access_token
from app.api.utils.password_handler import hash_password, verify_password
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
import os

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user from JWT token"""
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
        ALGORITHM = "HS256"
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return {"username": username}
    except JWTError:
        raise credentials_exception


class AuthService:
    def __init__(self):
        self.user_dao = UserDAO()

    def signup(self, user: UserSignup):
        if self.user_dao.get_by_username(user.username):
            return None
        
        hashed_password = hash_password(user.password)
        new_user = self.user_dao.create(user, hashed_password)
        token = create_access_token({"sub": user.username})
        
        return {"access_token": token, "token_type": "bearer", "user": new_user}

    def login(self, user: UserLogin):
        db_user = self.user_dao.get_by_username(user.username)
        if not db_user or not verify_password(user.password, db_user["password"]):
            return None
        
        token = create_access_token({"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}
