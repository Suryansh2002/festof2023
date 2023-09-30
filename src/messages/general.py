from enum import Enum
from typing import List, Optional

from uagents import Model


class UAgentResponseType(Enum):
    ERROR = "error"
    MESSAGE = "message"


class UAgentResponse(Model):
    type: UAgentResponseType
    message: Optional[str] = None
