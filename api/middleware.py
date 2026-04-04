from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
import logging


def init_middleware(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger = logging.getLogger("uvicorn.access")

    @app.middleware("http")
    async def log_requests(request, call_next):
        logger.info(f"{request.method} {request.url}")
        response = await call_next(request)
        return response
