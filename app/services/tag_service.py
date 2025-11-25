from typing import List
from app.database import get_database

class TagService:
    def __init__(self):
        self.collection_name = "posts"
    
    async def get_all_tags(self) -> List[str]:
        """Get list of all unique tags from posts"""
        db = get_database()
        collection = db[self.collection_name]
        
        # Use MongoDB aggregation to get distinct tags
        pipeline = [
            {"$unwind": "$tags"},
            {"$group": {"_id": "$tags"}},
            {"$sort": {"_id": 1}}
        ]
        
        tags = []
        async for doc in collection.aggregate(pipeline):
            tags.append(doc["_id"])
        
        return tags