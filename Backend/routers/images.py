# routers/images.py
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
import shutil
from sqlalchemy.orm import Session
import crud, schemas, database
from datetime import datetime
import os

import schemas, crud, auth, database, models
from cnn_loader import predict_from_bytes
from storage import save_image_bytes, create_thumbnail_from_bytes, IMAGES_DIR 

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/", response_model=schemas.ImageMetaResponse)
async def upload_image(
    patient_id: int = Form(...),
    current_user: models.HealthcareWorker = Depends(auth.get_current_active_user),
    notes: str = Form(""),
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    # 1 Ownership check
    patient = crud.get_patient(db, patient_id)
    if not patient or patient.created_by != current_user.hcw_id:
        raise HTTPException(status_code=403, detail="Not authorized to upload images for this patient")

    # 2 Read file into memory
    contents = await file.read()

    file_path = os.path.join(UPLOAD_DIR, f"{datetime.utcnow().timestamp()}_{file.filename}")
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    thumbnail_full_path = create_thumbnail_from_bytes(contents)
    thumbnail_filename = os.path.basename(thumbnail_full_path)

    # 3 Save image
    image_in = schemas.ImageMetaCreate(
        patient_id=patient_id,
        uploaded_by=current_user.hcw_id,
        file_path=file_path,
        thumbnail_path=thumbnail_filename, 
        notes=notes
    )
    return crud.create_image(db, *image_in.dict())
