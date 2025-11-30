from typing import Literal, Optional

from fastapi import APIRouter, Header, Path, Query, Request

from app.services.post_service import PostService
from app.utils.errors import ResourceNotFoundError
from app.utils.i18n import format_date

router = APIRouter()
post_service = PostService()


def add_post_hateoas_links(post_id: str, owner_id: str, base_url: str) -> dict:
    """Add HATEOAS links to post"""
    return {
        "self": {"href": f"{base_url}/api/v1/posts/{post_id}"},
        "owner": {"href": f"{base_url}/api/v1/users/{owner_id}"},
        "comments": {"href": f"{base_url}/api/v1/comments?post={post_id}"},
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


@router.get("")
async def get_posts(
    request: Request,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Literal["publishDate", "likes"] = Query("publishDate"),
    sort_order: SortOrder = Query(SortOrder.DESC),
    search: Optional[str] = Query(None),
    accept_language: Optional[str] = Header("en"),
):
    """Get list of posts with formatted dates"""
    filters = {}
    if search:
        filters["text"] = {"$regex": search, "$options": "i"}

    posts, total = await post_service.get_posts(page, limit, sort_by, sort_order.value, filters)

    # Extraire la langue
    lang = accept_language.split(",")[0].strip()[:2]

    base_url = str(request.base_url).rstrip("/")

    # Formater les dates pour chaque post
    posts_data = []
    for post in posts:
        post_dict = post.model_dump()

        # Formater publishDate
        if post_dict.get("publishDate"):
            post_dict["publishDate"] = format_date(post.publishDate, lang)

        # Formater owner si nécessaire
        if post_dict.get("owner") and isinstance(post_dict["owner"], dict):
            # Owner est déjà un dict, pas besoin de conversion
            pass

        # HATEOAS
        post_dict["_links"] = add_post_hateoas_links(post.id, post.owner.id, base_url)

        posts_data.append(post_dict)

    return {
        "data": posts_data,
        "total": total,
        "page": page,
        "limit": limit,
        "_links": add_pagination_links(
            base_url,
            "/api/v1/posts",
            page,
            limit,
            total,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
        ),
    }


@router.get("/user/{user_id}")
async def get_posts_by_user(
    request: Request,
    user_id: str = Path(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Literal["publishDate", "likes"] = Query("publishDate"),
    sort_order: SortOrder = Query(SortOrder.DESC),
    accept_language: Optional[str] = Header("en"),
):
    """Get posts by user with formatted dates"""
    filters = {"owner": user_id}
    posts, total = await post_service.get_posts(page, limit, sort_by, sort_order.value, filters)

    # Extraire la langue
    lang = accept_language.split(",")[0].strip()[:2]

    base_url = str(request.base_url).rstrip("/")

    # Formater les dates
    posts_data = []
    for post in posts:
        post_dict = post.model_dump()

        if post_dict.get("publishDate"):
            post_dict["publishDate"] = format_date(post.publishDate, lang)

        post_dict["_links"] = add_post_hateoas_links(post.id, post.owner.id, base_url)
        posts_data.append(post_dict)

    return {
        "data": posts_data,
        "total": total,
        "page": page,
        "limit": limit,
        "_links": add_pagination_links(
            base_url,
            f"/api/v1/posts/user/{user_id}",
            page,
            limit,
            total,
            sort_by=sort_by,
            sort_order=sort_order,
        ),
    }


@router.get("/tag/{tag}")
async def get_posts_by_tag(
    request: Request,
    tag: str = Path(...),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    sort_by: Literal["publishDate", "likes"] = Query("publishDate"),
    sort_order: SortOrder = Query(SortOrder.DESC),
    accept_language: Optional[str] = Header("en"),
):
    """Get posts by tag with formatted dates"""
    filters = {"tags": tag}
    posts, total = await post_service.get_posts(page, limit, sort_by, sort_order.value, filters)

    # Extraire la langue
    lang = accept_language.split(",")[0].strip()[:2]

    base_url = str(request.base_url).rstrip("/")

    # Formater les dates
    posts_data = []
    for post in posts:
        post_dict = post.model_dump()

        if post_dict.get("publishDate"):
            post_dict["publishDate"] = format_date(post.publishDate, lang)

        post_dict["_links"] = add_post_hateoas_links(post.id, post.owner.id, base_url)
        posts_data.append(post_dict)

    return {
        "data": posts_data,
        "total": total,
        "page": page,
        "limit": limit,
        "_links": add_pagination_links(
            base_url,
            f"/api/v1/posts/tag/{tag}",
            page,
            limit,
            total,
            sort_by=sort_by,
            sort_order=sort_order,
        ),
    }


@router.get("/{post_id}")
async def get_post(
    request: Request,
    post_id: str = Path(...),
    accept_language: Optional[str] = Header("en"),
):
    """Get post by ID with formatted date"""
    post = await post_service.get_post_by_id(post_id)

    if not post:
        raise ResourceNotFoundError(f"Post with id {post_id} not found")

    # Extraire la langue
    lang = accept_language.split(",")[0].strip()[:2]

    # Convertir en dict
    post_dict = post.model_dump()

    # REMPLACER la date
    if post_dict.get("publishDate"):
        post_dict["publishDate"] = format_date(post.publishDate, lang)

    # HATEOAS
    base_url = str(request.base_url).rstrip("/")
    post_dict["_links"] = add_post_hateoas_links(post.id, post.owner.id, base_url)

    return post_dict


@router.post("", status_code=201)
async def create_post(
    request: Request,
    post_data: PostCreate,
    accept_language: Optional[str] = Header("en"),
):
    """Create new post"""
    post = await post_service.create_post(post_data)

    # Extraire la langue
    lang = accept_language.split(",")[0].strip()[:2]

    # Convertir en dict
    post_dict = post.model_dump()

    # REMPLACER la date
    if post_dict.get("publishDate"):
        post_dict["publishDate"] = format_date(post.publishDate, lang)

    # HATEOAS
    base_url = str(request.base_url).rstrip("/")
    post_dict["_links"] = add_post_hateoas_links(post.id, post.owner.id, base_url)

    return post_dict


@router.put("/{post_id}")
async def update_post(
    request: Request,
    post_id: str,
    post_data: PostUpdate,
    accept_language: Optional[str] = Header("en"),
):
    """Update post"""
    post = await post_service.update_post(post_id, post_data)

    if not post:
        raise ResourceNotFoundError(f"Post with id {post_id} not found")

    # Extraire la langue
    lang = accept_language.split(",")[0].strip()[:2]

    # Convertir en dict
    post_dict = post.model_dump()

    # REMPLACER la date
    if post_dict.get("publishDate"):
        post_dict["publishDate"] = format_date(post.publishDate, lang)

    # HATEOAS
    base_url = str(request.base_url).rstrip("/")
    post_dict["_links"] = add_post_hateoas_links(post.id, post.owner.id, base_url)

    return post_dict


@router.delete("/{post_id}", response_model=DeleteResponse)
async def delete_post(post_id: str, accept_language: Optional[str] = Header("en")):
    """Delete post"""
    success = await post_service.delete_post(post_id)

    if not success:
        raise ResourceNotFoundError(f"Post with id {post_id} not found")

    return DeleteResponse(id=post_id, message="Post deleted successfully")
