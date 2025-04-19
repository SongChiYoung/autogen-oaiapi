from dataclasses import dataclass
from pydantic import BaseModel
from typing import List, Optional
from autogen_agentchat.teams import BaseGroupChat


@dataclass
class SessionContext:
    """
    Dataclass for storing session context information.

    Extend this class to include additional session-related fields as needed.
    """