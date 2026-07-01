#defines how data is sent and received through the API (Pydantic models)
#when creating an account a JSON body { "age": 25, "gender": "M" } will be sent/received by FastAPI, to ensure that the age is in numbers we use pydantic. Also for secrity
#

# schemas.py
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime

"""
Create - used for POST endpoints (what the user sends).
Create HealthcareWorker user (POST /create_user)
Input Schema : HealthcareWorkerCreate - what the FastAPI gets from flutter, how the data should be like and then its automatically packaged as a JSON
Output Schema : HealthcareWorkerResponse - what the FastAPI sends to flutter from the database, 
(from_attributes = True, tells Pydantic that we will get SQLAlchemy object (with attributes), not a dict from the databse and thas okay)
"""
# HealthcareWorker
# #properties required during healthcare worker account creation
class HealthcareWorkerBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[str] = "doctor"

# Used for user registration or creating a new user
class HealthcareWorkerCreate(HealthcareWorkerBase):
    password: str  # plain password input from API # only used during registration

# Response schema (what we return to frontend) (read)
class HealthcareWorkerResponse(HealthcareWorkerBase):
    hcw_id: int
    created_at: datetime
    is_active: bool 

    class Config:
        from_attributes = True# allows returning SQLAlchemy models directly # lets Pydantic read data from SQLAlchemy model objects

class LoginRequest(BaseModel):
    username: str
    password: str

# Patient
"""
Operation - Create patient (POST /patients)
Input Schema - PatientCreate
Output Schema - PatientResponse 
"""
class PatientBase(BaseModel):
    patient_code: str
    age: Optional[int] = None
    gender: Optional[str] = None
    hospital_id: Optional[str] = None

class PatientCreate(PatientBase):
    pass #done by /patient/ endpoint - created_by: int  # foreign key to HealthcareWorker - healthcare worker id

class PatientResponse(PatientBase):
    patient_id: int
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True

class PatientListItem(BaseModel):
    patient_id: int
    patient_code: str
    age: Optional[int] = None
    gender: Optional[str] = None
    hospital_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class PatientListPage(BaseModel):
    items: List[PatientListItem]
    total: int
    skip: int
    limit: int

# schemas.py
class PatientUpdate(BaseModel):
    age: Optional[int] = None
    gender: Optional[str] = None
    hospital_id: Optional[str] = None
    # patient_code updates optional; keep guarded if needed
    patient_code: Optional[str] = None


#ImageMeta
"""
Operation - Predict (POST /predict)
Input Schema - (file upload + query params)
Output Schema - PredictionResponse
"""
class ImageMetaBase(BaseModel):
    file_path: str
    thumbnail_path: Optional[str] = None
    notes: Optional[str] = None

class ImageMetaCreate(ImageMetaBase):
    patient_id: int
    uploaded_by: int

class ImageMetaResponse(ImageMetaBase):
    image_id: int
    patient_id: int
    uploaded_by: int
    upload_date: datetime

    class Config:
        from_attributes = True


# Prediction Schemas
"""
Operation - Predict (POST /predict)
Input Schema - (file upload + query params)
Output Schema - PredictionResponse
"""

class PredictionBase(BaseModel):
    predicted_class: str
    confidence_score: Optional[float] = None

class PredictionCreate(PredictionBase):
    image_id: int
    patient_id: int
    hcw_id: int

class PredictionResponse(PredictionBase): #it is returning the ids i want patient code and hcw username only
    predicted_class: str
    confidence_score: float
    image: Optional[ImageMetaResponse] = None 
    """
    {
  "predicted_class": "ALL",
  "confidence_score": 97.5,
  "image": {
      "file_path": "uploaded_images/20251129_xxx.jpg",
      "thumbnail_path": "thumbs/thumb_20251129_xxx.jpg"
  }
}

    """

    class Config:
        from_attributes = True

# Token Schema - for authentication
"""
Operation - Login (POST /token)
Input Schema - (handled by FastAPI's OAuth2 form)
Output Schema - Token
"""
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    sub: Optional[str] = None

# Combined / Nested Schemas
"""
Operation - Get patient history (GET /patient/{id}/predictions)
Input Schema - 
Output Schema - List[PredictionResponse]
"""
class PatientWithPredictions(PatientResponse):
    patient_code: str
    predictions: List[PredictionResponse] = []

    class Config:
        from_attributes = True

"""
| Schema            | Used for                                              | Example Endpoint                |
| ----------------- | ----------------------------------------------------- | ------------------------------- |
| `PatientCreate`   | POST request input                                    | Create a new patient            |
| `PatientResponse` | Internal response (includes created_by, patient_code) | Admin dashboard or internal API |
| `PatientOut`      | External/public response (only necessary fields)      | Flutter frontend                |


| Schema Name                      | Used For               | Example Endpoint                        |
| -------------------------------- | ---------------------- | --------------------------------------- |
| `PatientCreate`                  | Input (POST body)      | `/patients` → user sends JSON to create |
| `PatientUpdate` *(optional)*     | Input (PATCH/PUT body) | `/patients/{id}` to update info         |
| `PatientResponse` / `PatientOut` | Output (GET response)  | `/patients/{id}` → API returns JSON     |

"""