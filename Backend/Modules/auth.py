#Handles password hashing (bcrypt), JWT creation, and user authentication logic.

#auth.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import List, Optional

import models, database, crud

SECRET_KEY = "SENIORDESIGNPROJECT2ALLAPPSASNSA" ## replace with os.environ variable in production
ALGORITHM = "HS256" #HMAC-SHA256 (symmetric).
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")# for hashing
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/loginnow")#Bearer is the token we are going to get back from OAuth

# Password / Token utils

def hash_password(password: str) -> str:
    #print("Inside hash_password()")
    #print("  type(password):", type(password))
    #print("  password repr:", repr(password))
    #print("  str(password):", str(password))
    #print("  len(str(password)):", len(str(password)))
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool: #if return true the pasword matches
    return pwd_context.verify(plain_password, hashed_password)

#generate a token
def create_access_token(data: dict, expires_delta: timedelta | None = None): # user should pass like timedelta(minutes=10)
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})#dict
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Dependency
# verifying a token, if i am logged into the API, a user deltes itself and i am the user, then 
# it locks me out of the account. and also to ensire the token is valid so i can do stuff in the account 
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials (token invalid or expired)",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        sub = payload.get("sub")#sub is the username, sub contains the json web token
        if sub is None:
            raise credentials_exception
        hcw_id = int(sub)
    except JWTError:
        raise credentials_exception

    HealthcareWorker = crud.get_HealthcareWorker(db, hcw_id)
    if not HealthcareWorker:
        raise credentials_exception
    return HealthcareWorker

async def get_current_active_user(current_user: models.HealthcareWorker = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
