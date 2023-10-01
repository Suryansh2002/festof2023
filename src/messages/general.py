from enum import Enum
from typing import Optional

from uagents import Model


class UAgentResponseType(Enum):
    """
    This class is used to define the type of response sent by the agent.

    Attributes:
        ERROR (str): Error message
        MESSAGE (str): Success message
    """

    ERROR = "error"
    MESSAGE = "message"


class UAgentResponse(Model):
    """
    This class is used to define the response sent by the agent.

    Attributes:
        type (UAgentResponseType): Type of response
        message (Optional[str]): Message sent by the agent

    """

    type: UAgentResponseType
    message: Optional[str] = None
