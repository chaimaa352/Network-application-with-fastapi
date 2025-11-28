from starlette.middleware.base import BaseHTTPMiddleware


class BrotliMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, minimum_size: int = 1000):
        super().__init__(app)
        self.minimum_size = minimum_size

    async def dispatch(self, request, call_next):
        return await call_next(request)
