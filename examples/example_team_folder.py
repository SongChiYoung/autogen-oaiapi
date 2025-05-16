from autogen_oaiapi.server import Server
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination

"""
Load team from folder and you can see a round_robin_group_chat.json file.
It will make the round_robin_group_chat team to be availble passing model attribute in the request body data

Running this curl command will trigger the round_robin_group_chat team
curl 'http://0.0.0.0:8001/v1/chat/completions' \
  -H 'Content-Type: application/json' \
  -H 'accept: application/json' \
  --data-raw $'{\n  "session_id": "string",\n  "messages": [\n    {\n      "role": "user",\n      "content": "Calculate 1 + 1"\n    }\n  ],\n  "stream": false,\n  "model": "round_robin_group_chat"\n}'

You can see the response from the team in the response body, for example:
{
    "id":"chatcmpl-c07905dac4774dea9ae567cf1eb46e38","object":"chat.completion","created":1747262769,
    "model":"round_robin_group_chat",
    "choices":[
        {"index":0,"message":{"role":"assistant","content":"Calculate 1 + 1"},"finish_reason":"stop"},
        {"index":0,"message":{"role":"assistant","content":"RULES:\n- You have provided the expected response for the tool call\n- The calculation result is 2.0 (1 + 1)"},"finish_reason":"stop"}
    ],
    "usage":{"prompt_tokens":647,"completion_tokens":30,"total_tokens":0}
}

To fully run this example, you should have a local LLM running on http://localhost:1234/v1. 
You can use LM Studio or Ollama to run a local LLM.
"""
server = Server(team='examples/agents', source_select="writer")
server.run(port=8001)