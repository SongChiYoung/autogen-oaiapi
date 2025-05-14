from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from autogen_oaiapi.app.routes.v1.chat import router as chat_router
from autogen_oaiapi.app.routes.v1.models import router as models_router

def register_routes(app: FastAPI, prefix: str = "/v1") -> None:
    """Register API routes for the FastAPI application."""
    api_router = APIRouter()
    api_router.include_router(chat_router)
    api_router.include_router(models_router)
    app.include_router(api_router, prefix=prefix)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )