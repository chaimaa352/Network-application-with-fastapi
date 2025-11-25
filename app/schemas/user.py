from pydantic import BaseModel, Field, EmailStr, field_validator
from typing import Optional
from datetime import datetime
from enum import Enum

class TitleEnum(str, Enum):
    MR = "mr"
    MISS = "miss"
    DR = "dr"
    NONE = ""

class Location(BaseModel):
    """Location model"""
    street: str = Field(..., min_length=5, max_length=100)
    city: str = Field(..., min_length=2, max_length=30)
    state: str = Field(..., min_length=2, max_length=30)
    country: str = Field(..., min_length=2, max_length=30)
    timezone: str = Field(..., pattern=r'^[+-]\d{1,2}:\d{2}$')

class UserPreview(BaseModel):
    """User Preview - used in lists"""
    id: str
    title: TitleEnum = TitleEnum.NONE
    firstName: str = Field(..., min_length=2, max_length=50)
    lastName: str = Field(..., min_length=2, max_length=50)
    picture: str
    _links: Optional[dict] = None

class UserCreate(BaseModel):
    """User Create - for POST requests"""
    title: TitleEnum = TitleEnum.NONE
    firstName: str = Field(..., min_length=2, max_length=50)
    lastName: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    dateOfBirth: Optional[datetime] = None
    phone: Optional[str] = None
    picture: Optional[str] = "https://randomuser.me/api/portraits/lego/1.jpg"
    location: Optional[Location] = None
    
    @field_validator('dateOfBirth')
    @classmethod
    def validate_date_of_birth(cls, v):
        if v:
            min_date = datetime(1900, 1, 1)
            if v < min_date or v > datetime.now():
                raise ValueError('Date of birth must be between 1900-01-01 and now')
        return v

class UserUpdate(BaseModel):
    """User Update - for PUT/PATCH requests"""
    title: Optional[TitleEnum] = None
    firstName: Optional[str] = Field(None, min_length=2, max_length=50)
    lastName: Optional[str] = Field(None, min_length=2, max_length=50)
    dateOfBirth: Optional[datetime] = None
    phone: Optional[str] = None
    picture: Optional[str] = None
    location: Optional[Location] = None

class UserFull(BaseModel):
    """User Full - complete user data"""
    id: str
    title: TitleEnum = TitleEnum.NONE
    firstName: str
    lastName: str
    email: EmailStr
    dateOfBirth: Optional[datetime] = None
    registerDate: datetime
    phone: Optional[str] = None
    picture: str
    location: Optional[Location] = None
    _links: Optional[dict] = None