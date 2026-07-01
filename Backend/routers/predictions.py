# routers/predictions.py
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import os
from datetime import datetime
from typing import Optional, List

import schemas, crud, auth, database,models
from cnn_loader import predict_from_bytes
from storage import save_image_bytes, create_thumbnail_from_bytes, IMAGES_DIR 

router = APIRouter(prefix="/predictions", tags=["Predictions"])

@router.post("/", response_model=schemas.PredictionResponse) 
async def predict_and_save(
    file: UploadFile = File(...),
    patient_code: str = Form(...),
    notes_before: Optional[str] = Form(None),
    notes_after: Optional[str] = Form(None),
    current_user: models.HealthcareWorker = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db),
):
    # 1️ Lookup patient
    patient = crud.get_patient_by_code(db, patient_code)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient not found for code '{patient_code}'")
    
    # Debugging ownership values
    print("DEBUG patient.created_by:", repr(patient.created_by), type(patient.created_by))
    print("DEBUG current_user.hcw_id:", repr(current_user.hcw_id), type(current_user.hcw_id))

    # 2️ Ownership check: only creator can predict
    if str(patient.created_by) != str(current_user.hcw_id):
        raise HTTPException(status_code=403, detail="Not authorized to predict for this patient")

    # 3️ Read and validate file
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    # 4️ Run model inference
    try:
        predicted_class, confidence, all_probs = await predict_from_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")

    # 5️ Save image + thumbnail
    try:
        file_path = save_image_bytes(contents, file.filename)
        thumb_abs_path = create_thumbnail_from_bytes(contents, file.filename)

        # Convert absolute path → relative for frontend
        thumb_name = os.path.basename(thumb_abs_path)
        thumbnail_path = f"thumbs/{thumb_name}"

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

    # 6️ Save to database
    image = crud.create_image(
        db=db,
        patient_id=patient.patient_id,
        uploaded_by=str(current_user.hcw_id),
        file_path=file_path,
        thumbnail_path=thumbnail_path,
        notes=notes_before
    )

    prediction = crud.create_prediction(
        db=db,
        image_id=image.image_id,
        patient_id=patient.patient_id,
        hcw_id=str(current_user.hcw_id),
        predicted_class=predicted_class,
        confidence_score=confidence,
        notes=notes_after
    )

    
    # 7️ Return response
    return schemas.PredictionResponse.model_validate(prediction, from_attributes=True)

@router.get("/recent", response_model=List[schemas.PredictionResponse])
def get_recent_predictions(
    limit: int = 5,
    current_user: models.HealthcareWorker = Depends(auth.get_current_active_user),
    db: Session = Depends(database.get_db)
):

    preds = crud.get_recent_predictions(db, current_user.hcw_id, limit)

    output = []
    # convert SQLAlchemy models to Pydantic
    for p in preds:
        item = schemas.PredictionResponse.model_validate(p, from_attributes=True)

        # inject extra fields
        item.patient_code = p.patient.patient_code if p.patient else None
        item.hcw_username = current_user.username

        result.append(item)

    return result

"""
@router.post("/", response_model=schemas.PredictionResponse) 
async def predict_and_save(
    file: UploadFile = File(...),
    patient_code: str = Form(...),
    hcw_username: str = Form(...),
    notes_before: Optional[str] = Form(None),
    notes_after: Optional[str] = Form(None),
    db: Session = Depends(database.get_db)
):

    """ """
    Workflow:
    - Flutter sends file + patient_code + hcw_username
    - Backend looks up both in DB
    - Runs inference
    - Saves image + prediction + notes
    - Returns prediction info to Flutter
    """ """

    # 1 Validate inputs
    if not patient_code or not hcw_username:
        raise HTTPException(status_code=400, detail="patient_code and hcw_username are required")

    # 2️ Lookup patient & healthcare worker by code/username
    patient = crud.get_patient_by_code(db, patient_code)
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient not found for code '{patient_code}'")

    hcw = crud.get_HealthcareWorker_by_username(db, hcw_username)
    if not hcw:
        raise HTTPException(status_code=404, detail=f"Healthcare worker not found for username '{hcw_username}'")

    # 3️ Read and validate file
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Empty file uploaded")

    # 4️ Run model inference
    try:
        predicted_class, confidence, all_probs = await predict_from_bytes(contents)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model inference failed: {str(e)}")

    # 5️ Save image + thumbnail
    try:
        file_path = save_image_bytes(contents, file.filename)
        thumbnail_path = os.path.basename(create_thumbnail_from_bytes(contents))
        print("Thumbnail filename:", thumbnail_path)
        thumbnail_filename = os.path.basename(thumbnail_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving image: {str(e)}")

    # 6️ Save to database
    image = crud.create_image(
        db=db,
        patient_id=patient.patient_id,
        uploaded_by=hcw.hcw_id,
        file_path=file_path,
        thumbnail_path=thumbnail_path,
        notes=notes_before
    )

    prediction = crud.create_prediction(
        db=db,
        image_id=image.image_id,
        patient_id=patient.patient_id,
        hcw_id=hcw.hcw_id,  
        predicted_class=predicted_class,
        confidence_score=confidence,
        model_version="ResNet50_v1",
        notes=notes_after
    )

    # 7️ Build and return response
    return schemas.PredictionResponse(
        prediction_id=prediction.prediction_id,
        predicted_class=prediction.predicted_class,
        confidence_score=prediction.confidence_score,
        model_version=prediction.model_version,
        notes=prediction.notes,
        created_at=prediction.created_at,
        image=schemas.ImageMetaResponse(
            image_id=image.image_id,
            patient_id=image.patient_id,
            uploaded_by=image.uploaded_by,
            file_path=image.file_path,
            thumbnail_path=thumbnail_path,
            upload_date=image.upload_date,
            notes=image.notes
        )
    )
"""