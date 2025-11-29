
# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "FastAPI REST API",
        "version": "1.0.0"
    }
