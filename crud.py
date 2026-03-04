from sqlalchemy.orm import Session
from sqlalchemy import and_
import models, schemas
from auth import get_password_hash
from datetime import datetime, timedelta

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


# ── Admin CRUD ────────────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session) -> dict:
    from sqlalchemy import func
    cutoff = datetime.utcnow() - timedelta(hours=24)
    total_users       = db.query(func.count(models.User.id)).scalar()
    verified_users    = db.query(func.count(models.User.id)).filter(models.User.is_verified == True).scalar()
    total_measurements = db.query(func.count(models.Measurement.id)).scalar()
    last_24h          = db.query(func.count(models.Measurement.id)).filter(
        models.Measurement.measured_at >= cutoff
    ).scalar()
    recent = (
        db.query(models.Measurement)
        .order_by(models.Measurement.measured_at.desc())
        .limit(10)
        .all()
    )
    return {
        "total_users": total_users,
        "verified_users": verified_users,
        "total_measurements": total_measurements,
        "last_24h_measurements": last_24h,
        "recent_measurements": recent,
    }


def get_all_users(db: Session):
    return db.query(models.User).order_by(models.User.created_at.desc()).all()


def get_user_with_measurements(db: Session, user_id: str):
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None, []
    measurements = (
        db.query(models.Measurement)
        .filter(models.Measurement.user_id == user_id)
        .order_by(models.Measurement.measured_at.desc())
        .all()
    )
    return user, measurements


def admin_force_set_password(db: Session, user_id: str, new_password: str) -> bool:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    user.hashed_password = get_password_hash(new_password)
    db.commit()
    return True


def admin_toggle_admin(db: Session, user_id: str) -> models.User | None:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return None
    user.is_admin = not user.is_admin
    db.commit()
    db.refresh(user)
    return user


def admin_delete_user(db: Session, user_id: str) -> bool:
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        return False
    db.query(models.Measurement).filter(models.Measurement.user_id == user_id).delete()
    db.delete(user)
    db.commit()
    return True


def get_all_measurements_anonymous(db: Session):
    """Tüm ölçümleri kişisel veri olmadan döndürür (AI dataset export)."""
    return (
        db.query(
            models.Measurement.id,
            models.Measurement.user_id,
            models.Measurement.value,
            models.Measurement.category,
            models.Measurement.measured_at,
            models.Measurement.notes,
        )
        .order_by(models.Measurement.measured_at.asc())
        .all()
    )
