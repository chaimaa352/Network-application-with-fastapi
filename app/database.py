"""
Database configuration with fallback for CI/CD environment
"""
import os

# Configuration conditionnelle pour MongoDB
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    HAS_MONGO = True
except ImportError:
    HAS_MONGO = False
    print("⚠️ MongoDB dependencies not available - running in CI mode")

# Variables d'environnement avec valeurs par défaut pour CI
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "test_db")

if HAS_MONGO:
    # Configuration MongoDB normale
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[MONGO_DB_NAME]
else:
    # Fallback pour CI/CD
    client = None
    db = None

async def connect_to_mongo():
    """Connect to MongoDB if available"""
    if HAS_MONGO:
        print("✅ Connecting to MongoDB...")
        # Test connection
        await client.admin.command('ping')
        print("✅ MongoDB connected successfully")
    else:
        print("⚠️ MongoDB not available - running in test mode")

async def close_mongo_connection():
    """Close MongoDB connection if available"""
    if HAS_MONGO and client:
        client.close()
        print("✅ MongoDB connection closed")

def get_database():
    """Get database instance"""
    return db
