from autogen_oaiapi.server import Server
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination
from autogen_oaiapi.manager.api_key import JsonKeyManager

client = OpenAIChatCompletionClient(
    model="gpt-4.1-nano"
)
agent1 = AssistantAgent(name="writer", model_client=client)
agent2 = AssistantAgent(name="editor", model_client=client)
team = RoundRobinGroupChat(
    participants=[agent1, agent2],
    termination_condition=TextMentionTermination("TERMINATE"),
)

key_manager = JsonKeyManager(json_path="./example_api_key_config.json")

server = Server(key_manager=key_manager)
server.model.register(
    name="TEST_TEAM",
    actor=team,
    source_select="writer",
)
server.run(port=8001)