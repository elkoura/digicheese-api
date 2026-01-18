from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.exceptions import global_exception_handler
from app.core.logging import get_logger, setup_logging
from app.routers import auth_router, health_router
from app.routers.admin_communes import router as admin_communes_router

app = FastAPI(title="API Admin CdC")

app.include_router(admin_communes_router)
logger = get_logger(__name__)


def create_app() -> FastAPI:
    settings = get_settings()

    setup_logging(settings.log_level)

    app = FastAPI(title=settings.app_name, debug=settings.debug)

    # Middleware CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Middleware de journalisation sécurité
    @app.middleware("http")
    async def security_logging_middleware(request: Request, call_next):
        # Journalise les tentatives d'authentification
        if request.url.path.endswith("/login") and request.method == "POST":
            logger.info(f"Login attempt from {request.client.host if request.client else 'unknown'}")
        response = await call_next(request)
        # Journalise les refus d'authentification
        if response.status_code == 401:
            logger.warning(f"Unauthorized access attempt to {request.url.path} from {request.client.host if request.client else 'unknown'}")
        return response

    # Gestionnaire d'exception global
    app.add_exception_handler(Exception, global_exception_handler)

    # Routes
    app.include_router(health_router, prefix=settings.api_prefix)
    app.include_router(auth_router, prefix=settings.api_prefix)
    app.include_router(admin_communes.router)
    return app


app = create_app()

