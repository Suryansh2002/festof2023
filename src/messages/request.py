from enum import StrEnum

from uagents import Model


class SendsTo(StrEnum):
    AGENT = "agent"
    EMAIL = "email"


# this class is used to request the temperature of a location
class TemperatureRequest(Model):
    email: str
    location: str
    minimum_temperature: int
    maximum_temperature: int
    sends_to: list[SendsTo]
