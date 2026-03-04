from sqlalchemy.orm import Session
from sqlalchemy import and_
import models, schemas
from auth import get_password_hash
from datetime import datetime

def get_user(db: Session, user_id: str):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        data_consent=user.data_consent,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_or_create_oauth_user(db: Session, email: str, full_name: str):
    user = get_user_by_email(db, email)
    if not user:
        user = models.User(
            email=email,
            full_name=full_name,
            hashed_password=None,
            data_consent=True,
            is_verified=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_measurements(db: Session, user_id: str, limit: int = 100):
    return db.query(models.Measurement).filter(models.Measurement.user_id == user_id).order_by(models.Measurement.measured_at.desc()).limit(limit).all()

def create_measurement(db: Session, measurement: schemas.MeasurementCreate, user_id: str):
    db_measurement = models.Measurement(
        **measurement.model_dump(),
        user_id=user_id
    )
    if not db_measurement.measured_at:
        db_measurement.measured_at = datetime.utcnow()
    db.add(db_measurement)
    db.commit()
    db.refresh(db_measurement)
    return db_measurement

def get_measurements_by_date_range(db: Session, user_id: str, start_date: datetime, end_date: datetime):
    return db.query(models.Measurement).filter(
        and_(
            models.Measurement.user_id == user_id,
            models.Measurement.measured_at >= start_date,
            models.Measurement.measured_at <= end_date
        )
    ).order_by(models.Measurement.measured_at.asc()).all()
