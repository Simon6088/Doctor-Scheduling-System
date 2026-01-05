from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from ..database import get_db
from ..models import User, RoleEnum
from ..schemas import TokenData
from ..core.security import SECRET_KEY, ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    # In future we can add active check
    return current_user

def get_current_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != RoleEnum.ADMIN:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user

def get_current_manager_user(current_user: User = Depends(get_current_user)):
    if current_user.role not in [RoleEnum.ADMIN, RoleEnum.DEPARTMENT_MANAGER]:
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user
