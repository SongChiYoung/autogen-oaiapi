from fastapi import APIRouter, Request
from autogen_oaiapi.base.types import ChatCompletionRequest, ChatCompletionResponse
from autogen_oaiapi.message.message_converter import convert_to_llm_messages
from autogen_oaiapi.message.response_builder import build_openai_response

router = APIRouter()

@router.post("/chat/completions", response_model=ChatCompletionResponse)
async def chat_completions(request: Request, body: ChatCompletionRequest):
    server = request.app.state.server
    team = await server.get_team(body.session_id)
    idx = server.output_idx
    source = server.source_select
    treminate_text = server.terminate_message
    llm_messages = convert_to_llm_messages(body.messages)
    print("========================")
    print(body)
    print("========================")
    request_model = body.model
    result = await team.run(task=llm_messages)
    # result = result.messages[-idx]
    return build_openai_response(request_model, result, treminate_text, idx, source)