from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
import os

class Database:
        client: Optional["AsyncIOMotorClient"] = None  # type: ignore

db = Database()

async def connect_to_mongo():
    """Connect to MongoDB"""
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB_NAME", "social_network")
    
    db.client = AsyncIOMotorClient(mongodb_url)
    
    # Test connection
    await db.client.admin.command('ping')
    print(f"Connected to MongoDB: {db_name}")
    
    # Create indexes
    database = db.client[db_name]
    
    # Users indexes
    await database.users.create_index([("email", ASCENDING)], unique=True)
    await database.users.create_index([("registerDate", DESCENDING)])
    
    # Posts indexes
    await database.posts.create_index([("publishDate", DESCENDING)])
    await database.posts.create_index([("owner", ASCENDING)])
    await database.posts.create_index([("tags", ASCENDING)])
    
    # Comments indexes
    await database.comments.create_index([("publishDate", DESCENDING)])
    await database.comments.create_index([("post", ASCENDING)])
    await database.comments.create_index([("owner", ASCENDING)])
    
    print("Database indexes created")

async def close_mongo_connection():
    """Close MongoDB connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    db_name = os.getenv("MONGODB_DB_NAME", "social_network")
    if not db.client:
        raise RuntimeError("MongoDB client is not connected. Call connect_to_mongo first.")
    return db.client[db_name]
