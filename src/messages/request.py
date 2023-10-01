from enum import StrEnum
from typing import Optional

from pydantic import Field
from uagents import Model


class SendsTo(StrEnum):
    """
    This class is used to define the destinations where the user wants to receive the temperature alert.

    Attributes:
        AGENT (str): Agent
        EMAIL (str): Email

    """

    AGENT = "agent"
    EMAIL = "email"


class TemperatureRequest(Model):
    """
    This class is used to request the temperature of a location.

    Attributes:
        email (Optional[str]): Email of the user
        location (str): Location for which temperature is requested
        minimum_temperature (int): Minimum temperature
        maximum_temperature (int): Maximum temperature
        sends_to (list[SendsTo]): List of destinations where the user wants to receive the temperature alert
    """

    email: Optional[str] = None
    location: str
    minimum_temperature: int
    maximum_temperature: int
    sends_to: list[SendsTo] = Field(default=[SendsTo.AGENT])
