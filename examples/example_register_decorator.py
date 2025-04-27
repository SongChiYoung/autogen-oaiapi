from typing import Callable, Union
from autogen_oaiapi.server import Server
from autogen_agentchat.agents import AssistantAgent, BaseChatAgent
from autogen_agentchat.teams import RoundRobinGroupChat, BaseGroupChat
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.conditions import TextMentionTermination

server = Server()

# Define ActorType alias
ActorType = Union[BaseChatAgent, BaseGroupChat]

# Define the builder function with proper type hints
def build_team() -> RoundRobinGroupChat:
    client = OpenAIChatCompletionClient(
        model="gpt-4.1-nano"
    )
    agent1 = AssistantAgent(name="writer", model_client=client)
    agent2 = AssistantAgent(name="editor", model_client=client)
    team = RoundRobinGroupChat(
        participants=[agent1, agent2],
        termination_condition=TextMentionTermination("TERMINATE"),
    )
    return team

# Register the builder function using the correct method
# Pass the builder function itself, not the result of calling it
server.model.register_model_info(name="TEST_TEAM_DECORATOR", builder=build_team, source_select="writer")

server.run(port=8001)