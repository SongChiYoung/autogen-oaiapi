import asyncio
from typing import Any, Callable, Dict, List, Optional, Union, AsyncGenerator, Sequence

from autogen_core.common import TaskResult, BaseActor, BaseAgent
from autogen_core.registration import RegisteredActor
from autogen_agentchat.agents import BaseChatAgent
from autogen_agentchat.teams import BaseGroupChat
from autogen_agentchat.conditions import TerminationCondition, get_termination_conditions, BaseTerminationCondition
from autogen_oaiapi.openai_types import ChatMessage
from autogen_oaiapi.message import return_last_message, ReturnMessage
from autogen_oaiapi.base.types import ModelInfo, ModelRegistry

ActorType = Union[BaseChatAgent, BaseGroupChat]
BuilderType = Callable[[], ActorType]

class ModelClient(ModelRegistry):
    def __init__(self, default_model_name: str = "autogen-baseteam") -> None:
        super().__init__()
        self.default_model_name = default_model_name

    def _get_actor(self, name: str) -> ActorType:
        actor_info = self._models.get(name)
        if not actor_info:
            raise ValueError(f"Model {name} is not registered.")
        return actor_info.builder()

    def _get_termination_texts(self, actor: ActorType) -> List[str]:
        term_cond: Optional[BaseTerminationCondition] = getattr(actor, "termination_condition", None)
        texts: List[str] = []
        if isinstance(term_cond, BaseTerminationCondition):
            conditions: List[BaseTerminationCondition] = get_termination_conditions(term_cond)
            for cond in conditions:
                text = getattr(cond, "_termination_text", None)
                if isinstance(text, str):
                    texts.append(text)
        return texts

    def register(self, actor: ActorType, **kwargs: Any) -> None:
        actor_name = getattr(actor, 'name', None)
        if not actor_name:
            print("Warning: Actor provided to register() has no 'name' attribute. Skipping registration.")
            return

        termination_texts = self._get_termination_texts(actor)
        builder: BuilderType = lambda: actor
        model_info = ModelInfo(name=actor_name, builder=builder, termination_texts=termination_texts, **kwargs)
        self._models[actor_name] = model_info

    def register_model_info(self, name: str, builder: BuilderType, **kwargs: Any) -> None:
        termination_texts: List[str] = []
        try:
            actor_instance = builder()
            termination_texts = self._get_termination_texts(actor_instance)
            del actor_instance
        except Exception as e:
            print(f"Warning: Could not determine termination texts for {name}: {e}")

        model_info = ModelInfo(name=name, builder=builder, termination_texts=termination_texts, **kwargs)
        self._models[name] = model_info

    def run_stream(self, messages: List[ChatMessage], name: Optional[str] = None) -> AsyncGenerator[Union[str, TaskResult], None]:
        model_name = name or self.default_model_name
        actor = self._get_actor(model_name)
        termination_texts = self._models[model_name].termination_texts

        async def stream_output() -> AsyncGenerator[Union[str, TaskResult], None]:
            final_result: Optional[TaskResult] = None
            if hasattr(actor, "run_stream") and callable(actor.run_stream):
                task_input: Union[str, Sequence[Dict[str, Any]]]
                if len(messages) > 0:
                    task_input = [{'role': msg.role, 'content': msg.content or ""} for msg in messages]
                else:
                    task_input = ""

                async for chunk in actor.run_stream(task=task_input):
                    if isinstance(chunk, str):
                        yield chunk
                    elif isinstance(chunk, TaskResult):
                        final_result = chunk
            else:
                print(f"Warning: Actor {model_name} does not support streaming. Running non-stream method.")
                non_stream_result = await self.run(messages, name)
                message_data, _, _, _ = return_last_message(non_stream_result, terminate_texts=termination_texts)
                content = message_data.content if isinstance(message_data, ReturnMessage) else str(message_data)
                yield content
                final_result = non_stream_result

            if final_result:
                yield final_result

        return stream_output()

    async def run(self, messages: List[ChatMessage], name: Optional[str] = None) -> TaskResult:
        model_name = name or self.default_model_name
        actor = self._get_actor(model_name)
        termination_texts = self._models[model_name].termination_texts

        task_input: Union[str, Sequence[Dict[str, Any]]]
        if len(messages) > 0:
            task_input = [{'role': msg.role, 'content': msg.content or ""} for msg in messages]
        else:
            task_input = ""

        result: TaskResult
        if hasattr(actor, "run") and callable(actor.run):
            run_result = await actor.run(task=task_input)
            if isinstance(run_result, TaskResult):
                result = run_result
            else:
                print(f"Warning: Actor {model_name} run() returned unexpected type {type(run_result)}. Creating basic TaskResult.")
                result = TaskResult(summary=str(run_result))
        else:
            print(f"Error: Actor {model_name} does not have a run method.")
            result = TaskResult(error=f"Actor {model_name} does not have a run method.")

        return result