from enum import Enum

from uagents import Model


class TemperatureCondition(Enum):
    """
    This class is used to define the temperature condition.

    Attributes:
        LOW (str): Low temperature
        HIGH (str): High temperature

    """

    LOW = "low"
    HIGH = "high"


class TemperatureWarn(Model):
    """
    This class is used to send the temperature alert.

    Attributes:
        location (str): Location for which temperature is requested
        temperature (float): Temperature of the location
        condition (TemperatureCondition): Temperature condition
        minimum_temperature (float): Minimum temperature
        maximum_temperature (float): Maximum temperature
    """

    location: str
    temperature: float
    condition: TemperatureCondition
    minimum_temperature: float
    maximum_temperature: float
