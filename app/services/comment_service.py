from typing import List, Tuple, Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_database
from app.schemas.comment import CommentCreate, Comment
from app.services.user_service import UserService
from app.utils.errors import BodyNotValidError, ResourceNotFoundError


class CommentService:
    def __init__(self):
        self.collection_name = "comments"
        self.user_service = UserService()

    async def _comment_dict_to_model(self, comment_dict: dict) -> Comment:
        """Convert MongoDB comment dict to Comment model"""
        # Get owner preview
        owner = await self.user_service.get_user_preview_by_id(comment_dict["owner"])
        if not owner:
            raise ResourceNotFoundError(f"User {comment_dict['owner']} not found")

        return Comment(
            id=str(comment_dict["_id"]),
            message=comment_dict["message"],
            owner=owner,
            post=comment_dict["post"],
            publishDate=comment_dict["publishDate"],
        )

    async def get_comments(
        self,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "publishDate",
        sort_order: str = "desc",
        filters: dict = None,
    ) -> Tuple[List[Comment], int]:
        """Get paginated list of comments"""
        db = get_database()
        collection = db[self.collection_name]

        query = filters if filters else {}

        # Validate ObjectIds if present
        if "owner" in query and not ObjectId.is_valid(query["owner"]):
            return [], 0
        if "post" in query and not ObjectId.is_valid(query["post"]):
            return [], 0

        total = await collection.count_documents(query)

        sort_direction = -1 if sort_order == "desc" else 1
        skip = (page - 1) * limit

        cursor = (
            collection.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit)
        )

        comments = []
        async for comment_dict in cursor:
            try:
                comments.append(await self._comment_dict_to_model(comment_dict))
            except ResourceNotFoundError:
                # Skip comments with invalid owners
                continue

        return comments, total

    async def get_comment_by_id(self, comment_id: str) -> Optional[Comment]:
        """Get comment by ID"""
        if not ObjectId.is_valid(comment_id):
            return None

        db = get_database()
        collection = db[self.collection_name]

        comment_dict = await collection.find_one({"_id": ObjectId(comment_id)})

        if not comment_dict:
            return None

        return await self._comment_dict_to_model(comment_dict)

    async def create_comment(self, comment_data: CommentCreate) -> Comment:
        """Create new comment"""
        db = get_database()
        collection = db[self.collection_name]

        # Verify owner exists
        owner = await self.user_service.get_user_preview_by_id(comment_data.owner)
        if not owner:
            raise BodyNotValidError(f"User with id {comment_data.owner} not found")

        # Verify post exists
        posts_collection = db["posts"]
        if not ObjectId.is_valid(comment_data.post):
            raise BodyNotValidError(f"Invalid post id {comment_data.post}")

        post = await posts_collection.find_one({"_id": ObjectId(comment_data.post)})
        if not post:
            raise BodyNotValidError(f"Post with id {comment_data.post} not found")

        # Prepare comment document
        comment_dict = comment_data.model_dump()
        comment_dict["publishDate"] = datetime.utcnow()

        # Insert comment
        result = await collection.insert_one(comment_dict)

        # Get created comment
        created_comment = await collection.find_one({"_id": result.inserted_id})

        return await self._comment_dict_to_model(created_comment)

    async def delete_comment(self, comment_id: str) -> bool:
        """Delete comment"""
        if not ObjectId.is_valid(comment_id):
            return False

        db = get_database()
        collection = db[self.collection_name]

        result = await collection.delete_one({"_id": ObjectId(comment_id)})

        return result.deleted_count > 0
