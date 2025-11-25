from fastapi import APIRouter, Request
from app.services.tag_service import TagService

router = APIRouter()
tag_service = TagService()

@router.get("")
async def get_tags(request: Request):
    """Get list of all tags"""
    tags = await tag_service.get_all_tags()
    base_url = str(request.base_url).rstrip('/')
    
    tags_with_links = []
    for tag in tags:
        tags_with_links.append({
            "tag": tag,
            "_links": {
                "self": {"href": f"{base_url}/api/v1/tags"},
                "posts": {"href": f"{base_url}/api/v1/posts/tag/{tag}"}
            }
        })
    
    return {
        "data": tags_with_links,
        "total": len(tags),
        "_links": {"self": {"href": f"{base_url}/api/v1/tags"}}
    }