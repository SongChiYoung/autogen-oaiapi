from fastapi import APIRouter, Request
from autogen_oaiapi.base.types import ModelResponse, ModelListRequest, ModelListResponse

router = APIRouter()

@router.get("/models", response_model=ModelListResponse)
async def chat_completions(request: Request):
    """
    Handles the OPTIONS request for the /chat/completions/models endpoint.
    Returns a list of available models.
    """
    # In this case, we are just returning an empty list of models
    return ModelListResponse(
        object="list",
        data=[
            ModelResponse(id="autogen", object="model", owned_by="autogen", created=0),
        ]
    )