from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from autogen_oaiapi.app.routes.v1.chat import router as chat_router
from autogen_oaiapi.app.routes.v1.models import router as models_router

def register_routes(app, server):
    api_router = APIRouter()
    api_router.include_router(chat_router, prefix="/v1")
    api_router.include_router(models_router, prefix="/v1")
    app.include_router(api_router)

    # server is passed to the app state for access in routes
    app.state.server = server

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # or restrict to specific origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )