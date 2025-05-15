import gc
import itertools
from typing import Dict, List, Callable, AsyncGenerator, Sequence, Literal
from autogen_agentchat.teams import BaseGroupChat
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.base import (
    TerminationCondition,
    AndTerminationCondition,
    OrTerminationCondition,
)
from autogen_agentchat.conditions import (
    TextMentionTermination,
)
from autogen_core import ComponentModel
from autogen_agentchat.messages import ChatMessage, BaseChatMessage, BaseAgentEvent
from autogen_agentchat.base import TaskResult
from autogenstudio.teammanager import TeamManager
from autogenstudio.datamodel.types import TeamResult
from autogen_agentchat.messages import TextMessage

from ..base.types import Registry, ReturnMessage, TOTAL_MODELS_NAME
from ..message import return_last_message


def get_termination_conditions(termination_condition: TerminationCondition) -> Sequence[str]:
    """
    Get the termination conditions from a TerminationCondition object.
    Args:
        termination_condition (TerminationCondition): The termination condition object.
    Returns:
        Sequence[str]: A list of termination conditions.
    """
    if isinstance(termination_condition, str):
        return [termination_condition]

    if isinstance(termination_condition, TextMentionTermination):
        return [termination_condition._termination_text]  # type: ignore
    
    if isinstance(termination_condition, OrTerminationCondition) or isinstance(termination_condition, AndTerminationCondition):
        _termination_conditions = [get_termination_conditions(condition) for condition in termination_condition._conditions]  # type: ignore
        return list(itertools.chain.from_iterable(_termination_conditions))
    
    return []


class Model:
    """
    Model is a class that manages the registration and execution of AutoGen GroupChat and Agent instances.
    It provides methods to register models, run them, and retrieve their results.
    """
    def __init__(self) -> None:
        self._registry: Dict[str, Registry] = {}

    def _register(
        self,
        name: str,
        actor: BaseGroupChat | BaseChatAgent | Dict | None,
        source_select: str | None = None,
        output_idx: int | None = None,
        termination_conditions: Sequence[str] | None = None,
    ) -> None:
        """
        Register a model with the given name and actor.
        Args:
            name (str): The name of the model.
            actor (BaseGroupChat | BaseChatAgent): The actor (GroupChat or Agent) to register.
            source_select (str | None): The source select for the model.
            output_idx (int | None): The output index for the model.
            termination_conditions (Sequence[str] | None): The termination conditions for the model.
        """
        
        if isinstance(actor, BaseGroupChat):
            actor_type = "team"
            actor_component = actor.dump_component()
        elif isinstance(actor, BaseChatAgent):
            actor_type = "agent"
            actor_component = actor.dump_component()
        elif isinstance(actor, Dict):
            # In case of a teammanager, we create a placeholder Model to hold the actor with Dict
            # containing the agent configuration from JSON file
            actor_component = ComponentModel(type="team", provider="autogen", config = actor)
            actor_type = "teammanager"
        else:
            raise TypeError("actor must be a AutoGen GroupChat(team) or Agent instance")
        
        registry = Registry(
            name=name,
            actor=actor_component,
            type=actor_type,
            source_select=source_select,
            output_idx=output_idx,
            termination_conditions=termination_conditions or [],
        )
        self._registry[name] = registry

    def register(
        self,
        name: str,
        source_select: str | None = None,
        output_idx: int | None = None,
        actor: BaseGroupChat | BaseChatAgent | None = None,
    ) -> Callable[..., None]:
        """
        Register a model with the given name and actor.
        Args:
            name (str): The name of the model.
            source_select (str | None): The source select for the model.
            output_idx (int | None): The output index for the model.
            actor (BaseGroupChat | BaseChatAgent | None): The actor (GroupChat or Agent) to register.
        Returns:
            Callable[..., None]: A decorator to register the model.
        """
        if name == TOTAL_MODELS_NAME:
            # log, now allowed name
            raise ValueError(f"name cannot be '{TOTAL_MODELS_NAME}', please use a different name")
        if source_select is not None and output_idx is not None:
            raise ValueError("source_select and output_idx cannot be used together")
        if source_select is None and output_idx is None:
            output_idx = 0
        # if actor is None:
            # If no actor is provided, return a decorator
        def decorator(builder: Callable[..., BaseGroupChat|BaseChatAgent]) -> None:
            actor = builder()
            if isinstance(actor, BaseGroupChat):
                self._register(name, actor, source_select, output_idx, termination_conditions=get_termination_conditions(actor._termination_condition))  # type: ignore
            elif isinstance(actor, BaseChatAgent):
                if output_idx is not None and output_idx != 0:
                    # log warning
                    pass
                self._register(name, actor, None, output_idx)
            else:
                raise TypeError("actor must be a AutoGen GroupChat(team) or Agent instance")
        if actor is not None:
            if isinstance(actor, Dict):
                # In case of a teammanager, actor will be a Dict with the agent configuration from JSON file
                self._register(name, actor, source_select, output_idx)
            else:
                # If an actor is provided, register it directly
                self._register(name, actor, source_select, output_idx, termination_conditions=get_termination_conditions(actor._termination_condition))  # type: ignore

        return decorator  # is okay?

    @property
    def model_list(self) -> List[str]:
        """
        Get the list of registered models.

        Returns:
            List[str]: List of model names.
        """
        return list(self._registry.keys())

    # @property
    def _get_actor(self, name: str) -> BaseGroupChat | BaseChatAgent:
        """
        Get the actor (GroupChat or Agent) by name.
        Args:
            name (str): The name of the model.
        Returns:
            BaseGroupChat | BaseChatAgent: The actor (GroupChat or Agent) instance.
        Raises:
            KeyError: If the model is not found in the registry.
            TypeError: If the actor is not a valid GroupChat or Agent instance.
        """
      
        if name not in self._registry:
            raise KeyError(f"model {name} not found in registry")
        dump = self._registry[name].actor
        if self._registry[name].type == "team":
            return BaseGroupChat.load_component(dump)
        elif self._registry[name].type == "agent":
            return BaseChatAgent.load_component(dump)
        elif self._registry[name].type == "teammanager":
            return TeamManager()
        else:
            raise TypeError("actor must be a AutoGen GroupChat(team) or Agent instance")
        
    async def run_stream(self, name: str, messages: Sequence[ChatMessage]) -> AsyncGenerator[ReturnMessage, None]:
        """
        Run the model with the given name and messages, streaming the results.
        Args:
            name (str): The name of the model.
            messages (Sequence[ChatMessage]): The messages to send to the model.
        Yields:
            AsyncGenerator[ReturnMessage, None]: The streamed results from the model.
        """
        actor = self._get_actor(name)
        len_messages = len(messages)
        message_count = 0
        if isinstance(actor, BaseGroupChat):
            yield ReturnMessage(content="<think>")

        message: BaseAgentEvent | BaseChatMessage | TaskResult | None = None
        team_config = {}
        if isinstance(actor, TeamManager):
            team_config = self._registry[name].actor.config['team_config']
        
        async for message in actor.run_stream(task=messages, team_config = team_config):
            if len_messages > message_count:
                message_count += 1
                continue
            if not isinstance(message, TaskResult):
                yield ReturnMessage(content=f"## [{message.source}]\n\n" + message.to_text())
        else:
            if isinstance(actor, BaseGroupChat):
                yield ReturnMessage(content="</think>")
            # at that point, the message is a TaskResult
            if isinstance(message, TaskResult):
                content, total_prompt_tokens, total_completion_tokens, total_tokens = return_last_message(
                    message,
                    source=self._registry[name].source_select,
                    idx=self._registry[name].output_idx,
                    terminate_texts=self._registry[name].termination_conditions,
                )
                yield ReturnMessage(
                    content=content,
                    total_completion_tokens=total_completion_tokens,
                    total_prompt_tokens=total_prompt_tokens,
                    total_tokens=total_tokens,
                )
            else:
                yield ReturnMessage(
                    content="Somthing went wrong, please try again.",
                    total_completion_tokens=0,
                    total_prompt_tokens=0,
                    total_tokens=0, 
                )
        gc.collect()
        gc.garbage.clear() 
        return
    
    async def run(self, name: str, messages: List[ChatMessage]) -> ReturnMessage | List[ReturnMessage]:
        """
        Run the model with the given name and messages, returning the result.
        Args:
            name (str): The name of the model.
            messages (List[ChatMessage]): The messages to send to the model.
        Returns:
            ReturnMessage: The result from the model.
        Raises:
            TypeError: If the actor is not a valid GroupChat or Agent instance.
        """
        actor = self._get_actor(name)
        message = ReturnMessage(content="Something went wrong, please try again.", total_completion_tokens=0, total_prompt_tokens=0, total_tokens=0)
        if isinstance(actor, BaseGroupChat):
            async for message in self.run_stream(name, messages):
                continue
            else:
                return message
        elif isinstance(actor, BaseChatAgent):
            result_message = await actor.run(task=messages)
            content, total_prompt_tokens, total_completion_tokens, total_tokens = return_last_message(
                result_message,
                source=self._registry[name].source_select,
                idx=self._registry[name].output_idx,
                terminate_texts=self._registry[name].termination_conditions,
            )
            return ReturnMessage(
                content=content,
                total_completion_tokens=total_completion_tokens,
                total_prompt_tokens=total_prompt_tokens,
                total_tokens=total_tokens,
            )
        elif isinstance(actor, TeamManager):
            result_message = await TeamManager().run(task=messages, team_config=self._registry[name].actor.config['team_config'])
            if isinstance(result_message, TeamResult):
                messages = []
                for message in result_message.task_result.messages:
                    content = ""
                    total_prompt_tokens = 0
                    total_completion_tokens = 0
                    total_tokens = 0
                    if tokens:=message.models_usage:
                        total_prompt_tokens += tokens.prompt_tokens
                        total_completion_tokens += tokens.completion_tokens
                    if isinstance(message, TextMessage):
                        content = message.to_text()
                    message_to_return = ReturnMessage(
                        content=content,
                        total_completion_tokens=total_completion_tokens,
                        total_prompt_tokens=total_prompt_tokens,
                        total_tokens=total_tokens,
                    )
                    messages.append(message_to_return)
            
            return messages
        else:
            raise TypeError("actor must be a AutoGen GroupChat(team) or Agent instance")