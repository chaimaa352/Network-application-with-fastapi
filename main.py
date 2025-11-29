from fastapi import FastAPI
from app.database import connect_to_mongo, close_mongo_connection

app = FastAPI(title="Network API", version="1.0.0")

@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

@app.get("/")
async def root():
    return {"message": "Network API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    from app.database import HAS_MONGO
    return {
        "status": "healthy",
        "mongo_available": HAS_MONGO,
        "message": "API is running" + (" with MongoDB" if HAS_MONGO else " in CI mode")
    }

# Import routes conditionally
try:
    from app.routes import network_routes
    app.include_router(network_routes.router, prefix="/api/v1")
    print("✅ Network routes loaded")
except ImportError as e:
    print(f"⚠️ Some routes not available: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
