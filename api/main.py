from fastapi import FastAPI

from api.routers import calculate as calculate_router
from api.routers import upload as upload_router
from api.routers import anomalies as anomalies_router
from api.routers import reports as reports_router
from api.routers import jobs as jobs_router

from api.middleware import init_middleware
from db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="Carbon Trace Kenya")

    # Register routers
    app.include_router(calculate_router.router, prefix="/api")
    app.include_router(upload_router.router, prefix="/api")
    app.include_router(anomalies_router.router, prefix="/api")
    app.include_router(reports_router.router, prefix="/api")
    app.include_router(jobs_router.router, prefix="/api")

    # Initialize middleware (CORS, logging)
    init_middleware(app)

    @app.on_event("startup")
    def on_startup():
        # ensure DB tables exist during development
        try:
            init_db()
        except Exception:
            # in production the DB may be migrated separately
            pass

    return app


app = create_app()


@app.get("/health")
async def health():
    return {"status": "ok"}
