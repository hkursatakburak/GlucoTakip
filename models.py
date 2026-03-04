import uuid
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime
import enum

class MeasurementCategory(str, enum.Enum):
    FASTING = "Açlık"
    POSTPRANDIAL = "Tokluk"
    BEDTIME = "Yatmadan Önce"
    RANDOM = "Rastgele"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    data_consent = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    measurements = relationship("Measurement", back_populates="owner")

class Measurement(Base):
    __tablename__ = "measurements"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    value = Column(Integer)
    measured_at = Column(DateTime, default=datetime.utcnow)
    category = Column(SQLEnum(MeasurementCategory))
    notes = Column(String, nullable=True)

    owner = relationship("User", back_populates="measurements")
