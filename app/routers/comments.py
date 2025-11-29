from fastapi import APIRouter, Query, Path, Request, Header
from typing import Optional, Literal
from app.schemas.comment import CommentCreate, Comment
from app.schemas.common import PaginatedResponse, DeleteResponse, SortOrder
from app.services.comment_service import CommentService
from app.utils.errors import ResourceNotFoundError

router = APIRouter()
comment_service = CommentService()


def add_comment_hateoas_links(
    comment_id: str, post_id: str, owner_id: str, base_url: str
) -> dict:
    """Add HATEOAS links to comment"""
    return {
        "self": {"href": f"{base_url}/api/v1/comments/{comment_id}"},
        "post": {"href": f"{base_url}/api/v1/posts/{post_id}"},
        "owner": {"href": f"{base_url}/api/v1/users/{owner_id}"},
    }


def add_pagination_links(
    base_url: str, endpoint: str, page: int, limit: int, total: int, **params
) -> dict:
    """Add HATEOAS pagination links"""
    total_pages = (total + limit - 1) // limit
    query_params = "&".join([f"{k}={v}" for k, v in params.items() if v is not None])
    query_string = f"&{query_params}" if query_params else ""

    links = {
        "self": {
            "href": f"{base_url}{endpoint}?page={page}&limit={limit}{query_string}"
        },
        "first": {"href": f"{base_url}{endpoint}?page=1&limit={limit}{query_string}"},
        "last": {
            "href": f"{base_url}{endpoint}?page={total_pages}&limit={limit}{query_string}"
        },
    }

    if page > 1:
        links["prev"] = {
            "href": f"{base_url}{endpoint}?page={page-1}&limit={limit}{query_string}"
        }
    if page < total_pages:
        links["next"] = {
            "href": f"{base_url}{endpoint}?page={page+1}&limit={limit}{query_string}"
        }

    return links


@router.get(
    "",
    response_model=PaginatedResponse[Comment],
    summary="Get list of comments",
    description="Get paginated list of all comments",
)
async def get_comments(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Literal["publishDate"] = Query("publishDate"),
    sort_order: SortOrder = Query(SortOrder.DESC),
    post: Optional[str] = Query(None, description="Filter by post ID"),
    user: Optional[str] = Query(None, description="Filter by user ID"),
    accept_language: Optional[str] = Header("en"),
):
    """Get list of comments"""
    filters = {}
    if post:
        filters["post"] = post
    if user:
        filters["owner"] = user

    comments, total = await comment_service.get_comments(
        page, limit, sort_by, sort_order.value, filters
    )

    base_url = str(request.base_url).rstrip("/")
    for comment in comments:
        comment._links = add_comment_hateoas_links(
            comment.id, comment.post, comment.owner.id, base_url
        )

    endpoint = "/api/v1/comments"
    return PaginatedResponse(
        data=comments,
        total=total,
        page=page,
        limit=limit,
        _links=add_pagination_links(
            base_url,
            endpoint,
            page,
            limit,
            total,
            sort_by=sort_by,
            sort_order=sort_order,
            post=post,
            user=user,
        ),
    )


@router.get(
    "/post/{post_id}",
    response_model=PaginatedResponse[Comment],
    summary="Get comments by post",
    description="Get paginated list of comments for a specific post",
)
async def get_comments_by_post(
    request: Request,
    post_id: str = Path(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Literal["publishDate"] = Query("publishDate"),
    sort_order: SortOrder = Query(SortOrder.DESC),
    accept_language: Optional[str] = Header("en"),
):
    """Get comments by post ID"""
    filters = {"post": post_id}
    comments, total = await comment_service.get_comments(
        page, limit, sort_by, sort_order.value, filters
    )

    base_url = str(request.base_url).rstrip("/")
    for comment in comments:
        comment._links = add_comment_hateoas_links(
            comment.id, comment.post, comment.owner.id, base_url
        )

    return PaginatedResponse(
        data=comments,
        total=total,
        page=page,
        limit=limit,
        _links=add_pagination_links(
            base_url,
            f"/api/v1/comments/post/{post_id}",
            page,
            limit,
            total,
            sort_by=sort_by,
            sort_order=sort_order,
        ),
    )


@router.get(
    "/user/{user_id}",
    response_model=PaginatedResponse[Comment],
    summary="Get comments by user",
    description="Get paginated list of comments for a specific user",
)
async def get_comments_by_user(
    request: Request,
    user_id: str = Path(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Literal["publishDate"] = Query("publishDate"),
    sort_order: SortOrder = Query(SortOrder.DESC),
    accept_language: Optional[str] = Header("en"),
):
    """Get comments by user ID"""
    filters = {"owner": user_id}
    comments, total = await comment_service.get_comments(
        page, limit, sort_by, sort_order.value, filters
    )

    base_url = str(request.base_url).rstrip("/")
    for comment in comments:
        comment._links = add_comment_hateoas_links(
            comment.id, comment.post, comment.owner.id, base_url
        )

    return PaginatedResponse(
        data=comments,
        total=total,
        page=page,
        limit=limit,
        _links=add_pagination_links(
            base_url,
            f"/api/v1/comments/user/{user_id}",
            page,
            limit,
            total,
            sort_by=sort_by,
            sort_order=sort_order,
        ),
    )


@router.post(
    "",
    response_model=Comment,
    status_code=201,
    summary="Create comment",
    description="Create a new comment",
)
async def create_comment(
    request: Request,
    comment_data: CommentCreate,
    accept_language: Optional[str] = Header("en"),
):
    """Create new comment"""
    comment = await comment_service.create_comment(comment_data)

    base_url = str(request.base_url).rstrip("/")
    comment._links = add_comment_hateoas_links(
        comment.id, comment.post, comment.owner.id, base_url
    )

    return comment


@router.delete(
    "/{comment_id}",
    response_model=DeleteResponse,
    summary="Delete comment",
    description="Delete comment by ID",
)
async def delete_comment(
    comment_id: str = Path(...), accept_language: Optional[str] = Header("en")
):
    """Delete comment by ID"""
    success = await comment_service.delete_comment(comment_id)

    if not success:
        raise ResourceNotFoundError(f"Comment with id {comment_id} not found")

    return DeleteResponse(id=comment_id, message="Comment deleted successfully")
