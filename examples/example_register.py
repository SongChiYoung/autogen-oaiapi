from autogen_oaiapi.server import Server
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination

client = OpenAIChatCompletionClient(
    model="gpt-4.1-nano"
)
agent1 = AssistantAgent(name="writer", model_client=client)
agent2 = AssistantAgent(name="editor", model_client=client)
team = RoundRobinGroupChat(
    participants=[agent1, agent2],
    termination_condition=TextMentionTermination("TERMINATE"),
)

server = Server()
server.model.register(
    name="TEST_TEAM",
    actor=team,
    source_select="writer",
)
server.run(port=8001)