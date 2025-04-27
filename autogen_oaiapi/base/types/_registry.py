from pydantic import BaseModel
from typing import Literal, Sequence
from autogen_core import ComponentModel

class Registry(BaseModel):
    name: str
    actor: ComponentModel
    source_select: str | None = None
    output_idx: int | None = None
    type: Literal["agent", "team"]
    termination_conditions: Sequence[str] = []


TOTAL_MODELS_NAME = "*"