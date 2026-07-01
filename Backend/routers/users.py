# users.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import schemas, crud, auth, database,models
from auth import get_current_active_user
"""
from auth import hash_password, verify_password
from models import HealthcareWorker, Patient, ImageMeta, Prediction
from schemas import ImageMetaCreate,ImageMetaResponse,PredictionCreate,PredictionResponse,PatientWithPredictions,HealthcareWorkerResponse,HealthcareWorkerCreate
from crud import *
from database import get_db
"""

router = APIRouter(prefix="/auth", tags=["auth"])

# Routes

@router.post("/register", response_model=schemas.HealthcareWorkerResponse)
def register_HealthcareWorker(hcworker: schemas. HealthcareWorkerCreate, db: Session = Depends(database.get_db)):
    print("Incoming worker object:", hcworker)
    print("worker.password:", hcworker.password)
    print("type(worker.password):", type(hcworker.password))
    existing = crud.get_HealthcareWorker_by_username(db, hcworker.username)
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed = auth.hash_password(str(hcworker.password))
    new_user = crud.create_HealthcareWorker(db, hcworker, hashed)
    return new_user


@router.post("/login", response_model=schemas.Token)
def login(request: schemas.LoginRequest, db: Session = Depends(database.get_db)):
    user = crud.get_HealthcareWorker_by_username(db, request.username)
    if not user or not auth.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # update last login via CRUD
    crud.update_last_login(db, user)

    access_token = auth.create_access_token(data={"sub": str(user.hcw_id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/loginnow", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = crud.get_HealthcareWorker_by_username(db, form_data.username)
    if not user or not auth.verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid username or password")

    crud.update_last_login(db, user)
    access_token = auth.create_access_token(data={"sub": str(user.hcw_id)})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/meprofile", response_model=schemas.HealthcareWorkerResponse)
def read_users_me(current_user: models.HealthcareWorker = Depends(get_current_active_user)):
    return current_user