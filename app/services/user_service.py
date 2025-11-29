from typing import List, Tuple, Optional
from datetime import datetime
from bson import ObjectId
from app.database import get_database
from app.schemas.user import UserCreate, UserUpdate, UserFull, UserPreview
from app.utils.errors import BodyNotValidError


class UserService:
    def __init__(self):
        self.collection_name = "users"

    def _user_dict_to_preview(self, user_dict: dict) -> UserPreview:
        """Convert MongoDB user dict to UserPreview"""
        return UserPreview(
            id=str(user_dict["_id"]),
            title=user_dict.get("title", ""),
            firstName=user_dict["firstName"],
            lastName=user_dict["lastName"],
            picture=user_dict.get("picture", ""),
        )

    def _user_dict_to_full(self, user_dict: dict) -> UserFull:
        """Convert MongoDB user dict to UserFull"""
        return UserFull(
            id=str(user_dict["_id"]),
            title=user_dict.get("title", ""),
            firstName=user_dict["firstName"],
            lastName=user_dict["lastName"],
            email=user_dict["email"],
            dateOfBirth=user_dict.get("dateOfBirth"),
            registerDate=user_dict["registerDate"],
            phone=user_dict.get("phone"),
            picture=user_dict.get("picture", ""),
            location=user_dict.get("location"),
        )

    async def get_users(
        self,
        page: int = 1,
        limit: int = 20,
        sort_by: str = "registerDate",
        sort_order: str = "desc",
        filters: dict = None,
    ) -> Tuple[List[UserPreview], int]:
        """Get paginated list of users"""
        db = get_database()
        collection = db[self.collection_name]

        # Build query
        query = filters if filters else {}

        # Count total
        total = await collection.count_documents(query)

        # Build sort
        sort_direction = -1 if sort_order == "desc" else 1

        # Get users with pagination
        skip = (page - 1) * limit
        cursor = (
            collection.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit)
        )

        users = []
        async for user_dict in cursor:
            users.append(self._user_dict_to_preview(user_dict))

        return users, total

    async def get_user_by_id(self, user_id: str) -> Optional[UserFull]:
        """Get user by ID"""
        if not ObjectId.is_valid(user_id):
            return None

        db = get_database()
        collection = db[self.collection_name]

        user_dict = await collection.find_one({"_id": ObjectId(user_id)})

        if not user_dict:
            return None

        return self._user_dict_to_full(user_dict)

    async def get_user_preview_by_id(self, user_id: str) -> Optional[UserPreview]:
        """Get user preview by ID"""
        if not ObjectId.is_valid(user_id):
            return None

        db = get_database()
        collection = db[self.collection_name]

        user_dict = await collection.find_one({"_id": ObjectId(user_id)})

        if not user_dict:
            return None

        return self._user_dict_to_preview(user_dict)

    async def create_user(self, user_data: UserCreate) -> UserFull:
        """Create new user"""
        db = get_database()
        collection = db[self.collection_name]

        # Check if email already exists
        existing = await collection.find_one({"email": user_data.email})
        if existing:
            raise BodyNotValidError(f"User with email {user_data.email} already exists")

        # Prepare user document
        user_dict = user_data.model_dump()
        user_dict["registerDate"] = datetime.utcnow()

        # Insert user
        result = await collection.insert_one(user_dict)

        # Get created user
        created_user = await collection.find_one({"_id": result.inserted_id})

        return self._user_dict_to_full(created_user)

    async def update_user(
        self, user_id: str, user_data: UserUpdate
    ) -> Optional[UserFull]:
        """Update user (email cannot be updated)"""
        if not ObjectId.is_valid(user_id):
            return None

        db = get_database()
        collection = db[self.collection_name]

        # Build update dict (only non-None values)
        update_dict = {k: v for k, v in user_data.model_dump().items() if v is not None}

        if not update_dict:
            # No fields to update, return current user
            return await self.get_user_by_id(user_id)

        # Update user
        result = await collection.find_one_and_update(
            {"_id": ObjectId(user_id)}, {"$set": update_dict}, return_document=True
        )

        if not result:
            return None

        return self._user_dict_to_full(result)

    async def delete_user(self, user_id: str) -> bool:
        """Delete user"""
        if not ObjectId.is_valid(user_id):
            return False

        db = get_database()
        collection = db[self.collection_name]

        result = await collection.delete_one({"_id": ObjectId(user_id)})

        return result.deleted_count > 0
