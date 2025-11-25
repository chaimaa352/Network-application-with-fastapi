from typing import List, Tuple, Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_database
from app.schemas.post import PostCreate, PostUpdate, PostFull, PostPreview
from app.services.user_service import UserService
from app.utils.errors import BodyNotValidError, ResourceNotFoundError

class PostService:
    def __init__(self):
        self.collection_name = "posts"
        self.user_service = UserService()
    
    async def _post_dict_to_preview(self, post_dict: dict) -> PostPreview:
        """Convert MongoDB post dict to PostPreview"""
        # Get owner preview
        owner = await self.user_service.get_user_preview_by_id(post_dict["owner"])
        if not owner:
            raise ResourceNotFoundError(f"User {post_dict['owner']} not found")
        
        # Truncate text for preview (6-50 chars)
        text = post_dict["text"]
        preview_text = text[:50] if len(text) > 50 else text
        
        return PostPreview(
            id=str(post_dict["_id"]),
            text=preview_text,
            image=post_dict.get("image", ""),
            likes=post_dict.get("likes", 0),
            tags=post_dict.get("tags", []),
            publishDate=post_dict["publishDate"],
            owner=owner
        )
    
    async def _post_dict_to_full(self, post_dict: dict) -> PostFull:
        """Convert MongoDB post dict to PostFull"""
        # Get owner preview
        owner = await self.user_service.get_user_preview_by_id(post_dict["owner"])
        if not owner:
            raise ResourceNotFoundError(f"User {post_dict['owner']} not found")
        
        return PostFull(
            id=str(post_dict["_id"]),
            text=post_dict["text"],
            image=post_dict.get("image", ""),
            likes=post_dict.get("likes", 0),
            link=post_dict.get("link"),
            tags=post_dict.get("tags", []),
            publishDate=post_dict["publishDate"],
            owner=owner
        )
    
    async def get_posts(
        self,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "publishDate",
        sort_order: str = "desc",
        filters: dict = None
    ) -> Tuple[List[PostPreview], int]:
        """Get paginated list of posts"""
        db = get_database()
        collection = db[self.collection_name]
        
        query = filters if filters else {}
        
        # If filtering by owner, validate it's a valid ObjectId
        if "owner" in query and not ObjectId.is_valid(query["owner"]):
            return [], 0
        
        total = await collection.count_documents(query)
        
        sort_direction = -1 if sort_order == "desc" else 1
        skip = (page - 1) * limit
        
        cursor = collection.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit)
        
        posts = []
        async for post_dict in cursor:
            try:
                posts.append(await self._post_dict_to_preview(post_dict))
            except ResourceNotFoundError:
                # Skip posts with invalid owners
                continue
        
        return posts, total
    
    async def get_post_by_id(self, post_id: str) -> Optional[PostFull]:
        """Get post by ID"""
        if not ObjectId.is_valid(post_id):
            return None
        
        db = get_database()
        collection = db[self.collection_name]
        
        post_dict = await collection.find_one({"_id": ObjectId(post_id)})
        
        if not post_dict:
            return None
        
        return await self._post_dict_to_full(post_dict)
    
    async def create_post(self, post_data: PostCreate) -> PostFull:
        """Create new post"""
        db = get_database()
        collection = db[self.collection_name]
        
        # Verify owner exists
        owner = await self.user_service.get_user_preview_by_id(post_data.owner)
        if not owner:
            raise BodyNotValidError(f"User with id {post_data.owner} not found")
        
        # Prepare post document
        post_dict = post_data.model_dump()
        post_dict["publishDate"] = datetime.utcnow()
        
        # Insert post
        result = await collection.insert_one(post_dict)
        
        # Get created post
        created_post = await collection.find_one({"_id": result.inserted_id})
        
        return await self._post_dict_to_full(created_post)
    
    async def update_post(self, post_id: str, post_data: PostUpdate) -> Optional[PostFull]:
        """Update post (owner cannot be updated)"""
        if not ObjectId.is_valid(post_id):
            return None
        
        db = get_database()
        collection = db[self.collection_name]
        
        # Build update dict
        update_dict = {k: v for k, v in post_data.model_dump().items() if v is not None}
        
        if not update_dict:
            return await self.get_post_by_id(post_id)
        
        # Update post
        result = await collection.find_one_and_update(
            {"_id": ObjectId(post_id)},
            {"$set": update_dict},
            return_document=True
        )
        
        if not result:
            return None
        
        return await self._post_dict_to_full(result)
    
    async def delete_post(self, post_id: str) -> bool:
        """Delete post"""
        if not ObjectId.is_valid(post_id):
            return False
        
        db = get_database()
        collection = db[self.collection_name]
        
        result = await collection.delete_one({"_id": ObjectId(post_id)})
        
        return result.deleted_count > 0