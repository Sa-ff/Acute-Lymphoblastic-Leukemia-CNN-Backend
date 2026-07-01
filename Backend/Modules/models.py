#Defines all the ORM models → each class = a table (e.g., User, Patient, Prediction, etc.)
#defines how data is stored in the database (SQLAlchemy ORM models).
#Patient(age=25, gender="M") stored in SQLite

# models.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, Text, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class HealthcareWorker(Base):
    __tablename__ = "healthcare_workers"
    hcw_id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    email = Column(String)
    role = Column(String, default="doctor")
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)  # For soft deletion
    last_login = Column(DateTime, nullable=True)

    #back_populates="uploader" → connects this relationship to the matching one in the ImageMeta class: uploader = relationship("HealthcareWorker", back_populates="uploaded_images")
    uploaded_images = relationship("ImageMeta", back_populates="uploader")#One healthcare worker can upload many images.
    #when I access some_worker.uploaded_images, SQLAlchemy automatically retrieves all the images that worker uploaded.
    
    predictions = relationship("Prediction", back_populates="healthcare_workers")#One healthcare worker can make many predictions.
    #easily access all predictions made by a healthcare worker

class Patient(Base):
    __tablename__ = "patients"
    patient_id = Column(Integer, primary_key=True, index=True)
    patient_code = Column(String, unique=True, nullable=False) 
    age = Column(Integer)
    gender = Column(String)
    hospital_id = Column(String)
    created_by = Column(Integer, ForeignKey("healthcare_workers.hcw_id"))
    created_at = Column(DateTime, default=datetime.utcnow) #function from Python’s datetime module that returns the current UTC (Universal Coordinated Time) timestamp.
    #Using UTC avoids timezone confusion between servers and users.
    #datetime.utcnow : Each record will automatically store the time it was created when inserted into the DB.
    is_active = Column(Boolean, default=True)  # Important for GDPR/HIPAA compliance

    images = relationship("ImageMeta", back_populates="patient")#One patient can have many uploaded images - list of many images
    predictions = relationship("Prediction", back_populates="patient")#One patient can have many predictions associated with them. Links to Prediction.patient.

class ImageMeta(Base):
    __tablename__ = "image_metadata"
    image_id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    uploaded_by = Column(Integer, ForeignKey("healthcare_workers.hcw_id"), nullable=False)
    file_path = Column(String, nullable=False)
    thumbnail_path = Column(String, nullable=True)#This column stores the path to a smaller (compressed) version of the uploaded image.
    #in Flutter app to display faster previews of uploaded images.

    upload_date = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)

    patient = relationship("Patient", back_populates="images")#each image to a patient, the image_id belongs to one patient
    uploader = relationship("HealthcareWorker", back_populates="uploaded_images")#This connects each image to the healthcare worker who uploaded it.
    predictions = relationship("Prediction", back_populates="image",cascade="all, delete-orphan")#Each image can have many predictions 

class Prediction(Base):
    __tablename__ = "predictions"
    prediction_id = Column(Integer, primary_key=True, index=True)
    image_id = Column(Integer, ForeignKey("image_metadata.image_id"), nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.patient_id"), nullable=False)
    hcw_id = Column(Integer, ForeignKey("healthcare_workers.hcw_id"), nullable=False)
    predicted_class = Column(String, nullable=False)
    confidence_score = Column(Float)
    model_version = Column(String, default="EfficientNet_v1")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    image = relationship("ImageMeta", back_populates="predictions")#Each prediction corresponds to one image.
    patient = relationship("Patient", back_populates="predictions")
    healthcare_workers = relationship("HealthcareWorker", back_populates="predictions")#Each prediction is made by one healthcare worker.
