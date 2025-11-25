from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.user import UserPreview

class PostCreate(BaseModel):
    """Post Create - for POST requests"""
    text: str = Field(..., min_length=6, max_length=1000)
    image: str
    likes: int = Field(default=0, ge=0)
    tags: List[str] = Field(default_factory=list)
    owner: str  # User ID
    link: Optional[str] = Field(None, min_length=6, max_length=200)

class PostUpdate(BaseModel):
    """Post Update - for PUT/PATCH requests"""
    text: Optional[str] = Field(None, min_length=6, max_length=1000)
    image: Optional[str] = None
    likes: Optional[int] = Field(None, ge=0)
    tags: Optional[List[str]] = None
    link: Optional[str] = Field(None, min_length=6, max_length=200)

class PostPreview(BaseModel):
    """Post Preview - used in lists"""
    id: str
    text: str
    image: str
    likes: int = 0
    tags: List[str] = []
    publishDate: datetime
    owner: UserPreview
    _links: Optional[dict] = None

class PostFull(BaseModel):
    """Post Full - complete post data"""
    id: str
    text: str
    image: str
    likes: int = 0
    link: Optional[str] = None
    tags: List[str] = []
    publishDate: datetime
    owner: UserPreview
    _links: Optional[dict] = None