from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.user import UserPreview


class CommentCreate(BaseModel):
    """Comment Create - for POST requests"""

    message: str = Field(..., min_length=2, max_length=500)
    owner: str  # User ID
    post: str  # Post ID


class Comment(BaseModel):
    """Comment - complete comment data"""

    id: str
    message: str = Field(..., min_length=2, max_length=500)
    owner: UserPreview
    post: str  # Post ID
    publishDate: datetime
    _links: Optional[dict] = None
