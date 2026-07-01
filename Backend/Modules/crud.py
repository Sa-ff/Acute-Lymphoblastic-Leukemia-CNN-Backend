# crud.py
from sqlalchemy.orm import Session, joinedload
from auth import hash_password, verify_password
import models  
import schemas
from datetime import datetime
from typing import List, Optional
from sqlalchemy import or_, func

# Healthcare USER CRUD

def get_HealthcareWorker_by_username(db: Session, username: str) -> Optional[models.HealthcareWorker]:
    return db.query(models.HealthcareWorker).filter(models.HealthcareWorker.username == username).first()

def get_HealthcareWorker(db: Session, hcw_id: int) -> Optional[models.HealthcareWorker]:
    return db.query(models.HealthcareWorker).filter(models.HealthcareWorker.hcw_id == hcw_id).first()

def create_HealthcareWorker(db: Session, HealthcareWorker: schemas.HealthcareWorkerCreate, hashed_password: str):
    db_HealthcareWorker = models.HealthcareWorker(
        username=HealthcareWorker.username,
        full_name=HealthcareWorker.full_name,
        email=HealthcareWorker.email,
        password_hash=hashed_password,
        role="doctor"
    )
    db.add(db_HealthcareWorker)
    db.commit()
    db.refresh(db_HealthcareWorker)
    return db_HealthcareWorker

def update_last_login(db: Session, healthcare_worker: models.HealthcareWorker) -> None:
    healthcare_worker.last_login = datetime.utcnow()
    db.commit()
    db.refresh(healthcare_worker)  # ensures the updated value is available immediately

# PATIENT CRUD

def create_patient(db: Session, patient: schemas.PatientCreate, created_by: int):
    db_patient = models.Patient(**patient.dict(), created_by=created_by)
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

def get_patient(db: Session, patient_id: int) -> Optional[models.Patient]:
    return db.query(models.Patient).filter(models.Patient.patient_id == patient_id).first()

def get_patient_by_code(db: Session, patient_code: str) -> Optional[models.Patient]:
    return db.query(models.Patient).filter(models.Patient.patient_code == patient_code).first()

def list_patients_for_hcw(db: Session, hcw_id: int, q: Optional[str], skip: int, limit: int):
    base = db.query(models.Patient).filter(models.Patient.created_by == hcw_id)
    if q:
        base = base.filter(
            or_(
                models.Patient.patient_code.ilike(f"%{q}%"),
                models.Patient.hospital_id.ilike(f"%{q}%"),
            )
        )
    total = base.with_entities(func.count(models.Patient.patient_id)).scalar()
    items = base.order_by(models.Patient.created_at.desc()).offset(skip).limit(limit).all()
    return items, total

def update_patient(db: Session, db_patient: models.Patient, payload: schemas.PatientUpdate):
    data = payload.dict(exclude_unset=True)
    for k, v in data.items():
        setattr(db_patient, k, v)
    db.commit()
    db.refresh(db_patient)
    return db_patient
# IMAGE CRUD

def create_image(db: Session, patient_id: int, uploaded_by: int, file_path: str,thumbnail_path: Optional[str] = None, notes: Optional[str] = None):
    image = models.ImageMeta(
        patient_id=patient_id,
        uploaded_by=uploaded_by,
        file_path=file_path,
        thumbnail_path=thumbnail_path,
        notes=notes,
        upload_date=datetime.utcnow()
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image

def get_image(db: Session, image_id: int) -> Optional[models.ImageMeta]:
    return db.query(models.ImageMeta).filter(models.ImageMeta.image_id == image_id).first()


# PREDICTION CRUD

def create_prediction(db: Session, image_id: int, patient_id: int, hcw_id: int, 
                      predicted_class: str, confidence_score: float,
                      notes: Optional[str] = None):
    pred = models.Prediction(
                        image_id=image_id,
                        patient_id=patient_id,
                        hcw_id=hcw_id,
                        predicted_class=predicted_class,
                        confidence_score=confidence_score,
                        notes=notes
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)
    return pred

def get_predictions_for_patient(db: Session, patient_id: int):#-> List[models.Prediction]
    return (
        db.query(models.Prediction)
        .options(joinedload(models.Prediction.image))
        .filter(models.Prediction.patient_id == patient_id)
        .order_by(models.Prediction.created_at.desc())
        .all()
    )

def get_recent_predictions(db: Session, hcw_id: int, limit: int = 5):
    return (
        db.query(models.Prediction)
        .options(joinedload(models.Prediction.patient)) 
        .filter(models.Prediction.hcw_id == hcw_id)
        .order_by(models.Prediction.created_at.desc())
        .limit(limit)
        .all()
    )

