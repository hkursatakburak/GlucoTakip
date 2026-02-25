from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from models import MeasurementCategory
import uuid

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    data_consent: bool = False

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Measurement Schemas
class MeasurementBase(BaseModel):
    value: int
    measured_at: Optional[datetime] = None
    category: MeasurementCategory
    notes: Optional[str] = None

class MeasurementCreate(MeasurementBase):
    pass

class MeasurementResponse(MeasurementBase):
    id: int
    user_id: str
    measured_at: datetime
    
    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
