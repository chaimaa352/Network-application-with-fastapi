"""Main entry point for Docker container."""

# Import app for uvicorn - this is used by the Docker CMD
from app.main import app as application  # noqa: F401

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000)
