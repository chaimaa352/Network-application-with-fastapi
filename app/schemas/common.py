from enum import Enum
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class SortOrder(str, Enum):
    """Sort order enum"""

    ASC = "asc"
    DESC = "desc"


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response"""

    data: List[T]
    total: int = Field(..., description="Total items in database")
    page: int = Field(..., description="Current page number")
    limit: int = Field(..., description="Number of items per page")
    _links: Optional[dict] = None

    class Config:
        json_schema_extra = {"example": {"data": [], "total": 100, "page": 1, "limit": 20}}


class DeleteResponse(BaseModel):
    """Response for delete operations"""

    id: str
    message: str = "Resource deleted successfully"
