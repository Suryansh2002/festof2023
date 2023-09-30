from enum import Enum
from typing import List, Optional

from uagents import Model


class UAgentResponseType(Enum):
    ERROR = "error"
    MESSAGE = "message"
    SELECT_FROM_OPTIONS = "select_from_options"
    FINAL_OPTIONS = "final_options"


class KeyValue(Model):
    key: str
    value: str


class UAgentResponse(Model):
    type: UAgentResponseType
    agent_address: Optional[str] = None
    message: Optional[str] = None
    options: Optional[List[KeyValue]] = None
    request_id: Optional[str] = None
