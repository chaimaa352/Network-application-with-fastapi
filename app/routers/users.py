from typing import Literal, Optional

from bson import ObjectId
from bson.errors import InvalidId

from app.schemas.common import DeleteResponse, PaginatedResponse, SortOrder
from app.services.user_service import UserService
from app.utils.errors import ParamsNotValidError, ResourceNotFoundError
from app.utils.i18n import format_date

router = APIRouter()
user_service = UserService()


def validate_user_id(user_id: str) -> str:
    """Validate MongoDB ObjectId format"""
    try:
        if not ObjectId.is_valid(user_id):
            raise ParamsNotValidError(
                param="user_id",
                value=user_id,
                issue="Must be a valid MongoDB ObjectId (24 hex characters)",
                expected_format="24-character hexadecimal string",
            )
        return user_id
    except (InvalidId, TypeError):
        raise ParamsNotValidError(
            param="user_id",
            value=user_id,
            issue="Must be a valid MongoDB ObjectId (24 hex characters)",
            expected_format="24-character hexadecimal string",
        )


def add_user_hateoas_links(user_id: str, base_url: str) -> dict:
    """Add HATEOAS links to user"""
    return {
        "self": {"href": f"{base_url}/api/v1/users/{user_id}"},
        "posts": {"href": f"{base_url}/api/v1/posts/user/{user_id}"},
        "comments": {"href": f"{base_url}/api/v1/comments/user/{user_id}"},
    }


def add_pagination_links(
    base_url: str, endpoint: str, page: int, limit: int, total: int, **params
) -> dict:
    """Add HATEOAS pagination links"""
    total_pages = (total + limit - 1) // limit
    query_params = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
    query_string = f"&{query_params}" if query_params else ""

    links = {
        "self": {"href": f"{base_url}{endpoint}?page={page}&limit={limit}{query_string}"},
        "first": {"href": f"{base_url}{endpoint}?page=1&limit={limit}{query_string}"},
        "last": {"href": f"{base_url}{endpoint}?page={total_pages}&limit={limit}{query_string}"},
    }

    if page > 1:
        links["prev"] = {"href": f"{base_url}{endpoint}?page={page-1}&limit={limit}{query_string}"}
    if page < total_pages:
        links["next"] = {"href": f"{base_url}{endpoint}?page={page+1}&limit={limit}{query_string}"}

    return links


@router.get("", response_model=PaginatedResponse[UserPreview])
async def get_users(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Literal["registerDate", "firstName", "lastName"] = Query("registerDate"),
    sort_order: SortOrder = Query(SortOrder.DESC),
    title: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    accept_language: Optional[str] = Header("en"),
):
    """Get list of users"""
    filters = {}
    if title:
        filters["title"] = title
    if search:
        filters["$or"] = [
            {"firstName": {"$regex": search, "$options": "i"}},
            {"lastName": {"$regex": search, "$options": "i"}},
            {"email": {"$regex": search, "$options": "i"}},
        ]

    users, total = await user_service.get_users(page, limit, sort_by, sort_order.value, filters)

    base_url = str(request.base_url).rstrip("/")
    for user in users:
        user._links = add_user_hateoas_links(user.id, base_url)

    return PaginatedResponse(
        data=users,
        total=total,
        page=page,
        limit=limit,
        _links=add_pagination_links(base_url, "/api/v1/users", page, limit, total),
    )


@router.get("/{user_id}")
async def get_user(user_id: str, request: Request, accept_language: Optional[str] = Header("en")):
    """Get user by ID with dates formatted according to language"""
    # Validate user_id format
    validate_user_id(user_id)

    user = await user_service.get_user_by_id(user_id)
    if not user:
        raise ResourceNotFoundError(resource="User", identifier=user_id, searched_by="id")

    # Extraire la langue
    lang = accept_language.split(",")[0].strip()[:2]

    # Convertir en dictionnaire
    user_dict = user.model_dump()

    # REMPLACER les dates ISO par les dates formatées
    if user_dict.get("registerDate"):
        user_dict["registerDate"] = format_date(user.registerDate, lang)

    if user_dict.get("dateOfBirth") and user.dateOfBirth:
        user_dict["dateOfBirth"] = format_date(user.dateOfBirth, lang)

    # HATEOAS
    base_url = str(request.base_url).rstrip("/")
    user_dict["_links"] = add_user_hateoas_links(user.id, base_url)

    return user_dict


@router.post("", status_code=201)
async def create_user(
    user_data: UserCreate,
    request: Request,
    accept_language: Optional[str] = Header("en"),
):
    """Create new user"""
    user = await user_service.create_user(user_data)

    # Extraire la langue
    lang = accept_language.split(",")[0].strip()[:2]

    # Convertir en dictionnaire
    user_dict = user.model_dump()

    # REMPLACER les dates
    if user_dict.get("registerDate"):
        user_dict["registerDate"] = format_date(user.registerDate, lang)

    if user_dict.get("dateOfBirth") and user.dateOfBirth:
        user_dict["dateOfBirth"] = format_date(user.dateOfBirth, lang)

    # HATEOAS
    base_url = str(request.base_url).rstrip("/")
    user_dict["_links"] = add_user_hateoas_links(user.id, base_url)

    return user_dict


@router.put("/{user_id}")
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    request: Request,
    accept_language: Optional[str] = Header("en"),
):
    """Update user"""
    # Validate user_id format
    validate_user_id(user_id)

    user = await user_service.update_user(user_id, user_data)
    if not user:
        raise ResourceNotFoundError(resource="User", identifier=user_id, searched_by="id")

    # Extraire la langue
    lang = accept_language.split(",")[0].strip()[:2]

    # Convertir en dictionnaire
    user_dict = user.model_dump()

    # REMPLACER les dates
    if user_dict.get("registerDate"):
        user_dict["registerDate"] = format_date(user.registerDate, lang)

    if user_dict.get("dateOfBirth") and user.dateOfBirth:
        user_dict["dateOfBirth"] = format_date(user.dateOfBirth, lang)

    # HATEOAS
    base_url = str(request.base_url).rstrip("/")
    user_dict["_links"] = add_user_hateoas_links(user.id, base_url)

    return user_dict


@router.delete("/{user_id}", response_model=DeleteResponse)
async def delete_user(user_id: str, accept_language: Optional[str] = Header("en")):
    """Delete user"""
    # Validate user_id format
    validate_user_id(user_id)

    success = await user_service.delete_user(user_id)
    if not success:
        raise ResourceNotFoundError(resource="User", identifier=user_id, searched_by="id")
    return DeleteResponse(id=user_id)
