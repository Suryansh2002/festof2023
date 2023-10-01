from enum import Enum

from uagents import Model


class TemperatureCondition(Enum):
    LOW = "low"
    HIGH = "high"


class TemperatureWarn(Model):
    location: str
    temperature: float
    condition: TemperatureCondition
    minimum_temperature: float
    maximum_temperature: float
