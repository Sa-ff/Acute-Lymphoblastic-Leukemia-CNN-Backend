# routers/patients.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import schemas, crud, auth, database, models
from auth import get_current_active_user

router = APIRouter(prefix="/patients", tags=["Patients"])

@router.post("/", response_model=schemas.PatientResponse)
def create_patient(patient: schemas.PatientCreate, current_user: models.HealthcareWorker = Depends(get_current_active_user),
    db: Session = Depends(database.get_db)):
     # Find HCW by username, else use jwt to get the username-diff code 

    return crud.create_patient(db, patient,created_by=current_user.hcw_id)

@router.get("/code/{patient_id}", response_model=schemas.PatientWithPredictions)
def get_patient_with_predictions(patient_id: int,current_user: models.HealthcareWorker = Depends(auth.get_current_active_user), db: Session = Depends(database.get_db)):
    db_patient = crud.get_patient(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    # Strict ownership check
    if db_patient.created_by != current_user.hcw_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this patient")
    predictions = crud.get_predictions_for_patient(db, patient_id)
    #return {**db_patient.__dict__, "predictions": predictions}
    # Dynamically map predictions using Pydantic (from_attributes=True)
    predictions = [schemas.PredictionResponse(**vars(p)) for p in predictions]

    # Dynamically map the patient object, adding predictions
    return schemas.PatientWithPredictions(**{**vars(db_patient), "predictions": predictions})

@router.get("/{patient_code}", response_model=schemas.PatientWithPredictions)
def get_patient_by_code(patient_code: str, current_user: models.HealthcareWorker = Depends(auth.get_current_active_user), db: Session = Depends(database.get_db)):
    db_patient = crud.get_patient_by_code(db, patient_code)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Debugging ownership values
    print("DEBUG patient.created_by:", repr(db_patient.created_by), type(db_patient.created_by))
    print("DEBUG current_user.hcw_id:", repr(current_user.hcw_id), type(current_user.hcw_id))

    # Strict ownership check
    if db_patient.created_by != current_user.hcw_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this patient")
    
    # Get all predictions for this patient
    predictions = crud.get_predictions_for_patient(db, db_patient.patient_id)

    # Dynamically map predictions using Pydantic (from_attributes=True)
    #predictions = [schemas.PredictionResponse(**vars(p)) for p in predictions]
    predictions = [schemas.PredictionResponse.model_validate(p, from_attributes=True) for p in predictions]

    #print("Thumbnail path in response:", predictions[0].image.thumbnail_path)

    # Dynamically map the patient object, adding predictions
    return schemas.PatientWithPredictions(**{**vars(db_patient), "predictions": predictions})

@router.get("/patientslist", response_model=list[schemas.PatientResponse])
def list_patients(
    current_user: models.HealthcareWorker = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    # Only return patients created by this healthcare worker
    patients = (
        db.query(models.Patient)
        .filter(models.Patient.created_by == current_user.hcw_id)
        .all()
    )
    return patients

"""
@router.get("/patientlist", response_model=schemas.PatientListPage)
def list_my_patients(
    q: str | None = Query(None, description="Search by patient_code"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: models.HealthcareWorker = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    items, total = crud.list_patients_for_hcw(db, hcw_id=current_user.hcw_id, q=q, skip=skip, limit=limit)
    return schemas.PatientListPage(items=items, total=total, skip=skip, limit=limit)

@router.put("/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(
    patient_id: int,
    payload: schemas.PatientUpdate,
    current_user: models.HealthcareWorker = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    db_patient = crud.get_patient(db, patient_id)
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if db_patient.created_by != current_user.hcw_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this patient")

    updated = crud.update_patient(db, db_patient, payload)
    return updated


Strict ownership (above) → only the healthcare worker who created the patient can access them.

Shared access → if multiple healthcare workers should see the same patient, you'll need a 
linking table (e.g., patient_access) that defines which workers can access which patients.

Role-based access → e.g., doctors can see all patients, nurses only their own. You'd check 
current_user.role before allowing access.

For compliance (HIPAA/GDPR):strict ownership , Always enforce created_by == current_user.hcw_id. 

authentication:JWT ensures authentication, meaning?symmetric encryption  https://medium.com/@mohantyshyama/understanding-jwt-for-secure-authentication-a489e7d37165
authorisation: only the healthcare user who created the patient can view the patient. 

"""