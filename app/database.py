from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient

class Database:
    client: Optional[AsyncIOMotorClient] = None  # type: ignore

db = Database()

async def connect_to_mongo():
    db.client = AsyncIOMotorClient("mongodb://localhost:27017")

async def close_mongo_connection():
    if db.client:
        db.client.close()

def get_database():
    return db.client
