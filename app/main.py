from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from datetime import datetime
import time
import uuid

from app.database import connect_to_mongo, close_mongo_connection
from app.routers import users, posts, comments, tags
from app.middleware.compression import BrotliMiddleware
from app.middleware.cache import CacheControlMiddleware
from app.utils.errors import APIError
from app.utils.i18n import setup_i18n

# Lifecycle management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(" Starting application...")
    await connect_to_mongo()
    setup_i18n()
    print(" Application started successfully!")
    yield
    # Shutdown
    print(" Shutting down application...")
    await close_mongo_connection()
    print(" Application shutdown complete!")

# Create FastAPI app with versioning (Technique 1: URL Path)
app = FastAPI(
    title="Social Network API",
    description="REST API for Social Network Application",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    openapi_url="/api/v1/openapi.json"
)

# CORS Configuration (Requirement h)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8080",
        "https://yourdomain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Total-Count", "X-Page", "X-Limit"]
)

# Compression Middleware (Requirement j)
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(BrotliMiddleware, minimum_size=1000)

# Cache Control Middleware (Requirement i)
app.add_middleware(CacheControlMiddleware)

# Custom middleware for versioning (Technique 2: Custom Header)
@app.middleware("http")
async def version_middleware(request: Request, call_next):
    api_version = request.headers.get("X-API-Version", "1.0")
    request.state.api_version = api_version
    response = await call_next(request)
    response.headers["X-API-Version"] = api_version
    return response

# Performance monitoring middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Helper function to create standardized error responses
def create_error_response(
    code: str,
    message: str,
    status_code: int,
    path: str,
    method: str,
    details: any = None
):
    """Create standardized error response"""
    return {
        "error": {
            "code": code,
            "message": message,
            "statusCode": status_code,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "path": path,
            "method": method,
            "details": details
        }
    }

# Exception Handlers (Requirement d)

# 1. Handler pour les erreurs API personnalisées (PARAMS_NOT_VALID, RESOURCE_NOT_FOUND, etc.)
@app.exception_handler(APIError)
async def api_error_handler(request: Request, exc: APIError):
    """Handle custom API errors with full error structure"""
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            code=exc.code,
            message=exc.message,
            status_code=exc.status_code,
            path=str(request.url.path),
            method=request.method,
            details=exc.details
        )
    )

# 2. Handler pour les erreurs de validation Pydantic (BODY_NOT_VALID)
@app.exception_handler(RequestValidationError)
async def validation_error_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors (body validation)"""
    errors = []
    for error in exc.errors():
        # Extraire le nom du champ (sans "body")
        field_parts = [str(loc) for loc in error["loc"] if loc != "body"]
        field = ".".join(field_parts) if field_parts else "body"
        
        errors.append({
            "field": field,
            "value": error.get("input"),
            "issue": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content=create_error_response(
            code="BODY_NOT_VALID",
            message="Request body validation failed",
            status_code=400,
            path=str(request.url.path),
            method=request.method,
            details=errors
        )
    )

# 3. Handler pour les erreurs HTTP (notamment 404 PATH_NOT_FOUND)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions including 404 not found"""
    if exc.status_code == 404:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=create_error_response(
                code="PATH_NOT_FOUND",
                message="The requested endpoint does not exist",
                status_code=404,
                path=str(request.url.path),
                method=request.method,
                details={
                    "availableEndpoints": [
                        "GET /api/v1/users",
                        "GET /api/v1/users/{id}",
                        "POST /api/v1/users",
                        "PUT /api/v1/users/{id}",
                        "DELETE /api/v1/users/{id}",
                        "GET /api/v1/posts",
                        "GET /api/v1/posts/{id}",
                        "GET /api/v1/comments",
                        "GET /api/v1/tags"
                    ]
                }
            )
        )
    
    # Pour les autres erreurs HTTP
    return JSONResponse(
        status_code=exc.status_code,
        content=create_error_response(
            code="HTTP_ERROR",
            message=exc.detail,
            status_code=exc.status_code,
            path=str(request.url.path),
            method=request.method,
            details=None
        )
    )

# 4. Handler pour les erreurs serveur non gérées (SERVER_ERROR)
@app.exception_handler(Exception)
async def server_error_handler(request: Request, exc: Exception):
    """Handle unexpected server errors"""
    error_id = str(uuid.uuid4())
    
    # Log l'erreur (en production, utilisez un vrai logger)
    print(f"[ERROR {error_id}] {type(exc).__name__}: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=create_error_response(
            code="SERVER_ERROR",
            message="An internal server error occurred",
            status_code=500,
            path=str(request.url.path),
            method=request.method,
            details={
                "errorId": error_id,
                "message": "Please try again later or contact support if the issue persists"
            }
        )
    )

# Include routers with versioning
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["Posts"])
app.include_router(comments.router, prefix="/api/v1/comments", tags=["Comments"])
app.include_router(tags.router, prefix="/api/v1/tags", tags=["Tags"])

# Root endpoint with HATEOAS
@app.get("/api/v1", tags=["Root"])
async def root():
    """Root endpoint with HATEOAS links (Requirement l)"""
    return {
        "message": "Welcome to Social Network API",
        "version": "1.0.0",
        "_links": {
            "self": {"href": "/api/v1"},
            "users": {"href": "/api/v1/users"},
            "posts": {"href": "/api/v1/posts"},
            "comments": {"href": "/api/v1/comments"},
            "tags": {"href": "/api/v1/tags"},
            "docs": {"href": "/api/v1/docs"}
        }
    }

# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)