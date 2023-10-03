"""
This file is responsible for connecting to the database and performing CRUD operations on it.
It also contains the Data class which is used to define the data stored in the database.

"""

import asyncio
import os
from typing import Optional

from motor.motor_asyncio import AsyncIOMotorClient  # motor is an async mongodb driver
from odmantic.engine import AIOEngine
from odmantic.field import Field
from odmantic.model import Model

from messages import SendsTo

# odmantic is a ODM (object document mapper) for pymongo,motor


MONGODB_URL = os.getenv("MONGODB_URL")
assert MONGODB_URL, "Please set the MONGODB_URL environment variable"


class Data(Model):
    """
    This class is used to define the data stored in the database.

    Attributes:
        address (str): Address of the agent
        email (Optional[str]): Email of the user
        lat (float): Latitude of the location
        lon (float): Longitude of the location
        location (str): Location
        minimum_temperature (float): Minimum temperature
        maximum_temperature (float): Maximum temperature
        sends_to (list[SendsTo]): List of destinations where the user wants to receive the temperature alert

    """

    address: str = Field(primary_field=True)
    email: Optional[str] = Field(default=None)
    lat: float
    lon: float
    location: str
    minimum_temperature: float
    maximum_temperature: float
    sends_to: list[SendsTo] = Field(default=[SendsTo.AGENT])


class Database:
    """
    This class is used to connect to the database and perform CRUD operations on it.

    Attributes:
        client (AsyncIOMotorClient): AsyncIOMotorClient object
        engine (AIOEngine): AIOEngine object
        _started (bool): True if the database is connected, False otherwise

    """

    def __init__(self) -> None:
        self._started = False

    async def connect(self):
        """
        This function is used to connect to the database.

        Returns:
            None

        """
        if self._started:
            return  # do not proceed if database is already connected

        # connect to the database
        self.client = AsyncIOMotorClient(
            MONGODB_URL, io_loop=asyncio.get_running_loop()
        )
        self.engine = AIOEngine(
            self.client, database="temperature_agent"
        )  # create engine
        self._started = True

    async def find_all(self):
        """
        This function is used to fetch all the users from the database.

        Yields:
            Data: Data object

        """
        await self.connect()  # connect to the database
        async for data in self.engine.find(Data):  # fetch all users from database
            yield data

    async def insert(
        self,
        address: str,
        lat: float,
        lon: float,
        location: str,
        min_temp: float,
        max_temp: float,
        sends_to: list[SendsTo],
        email: Optional[str] = None,
    ):
        """
        This function is used to insert a user into the database.

        Args:
            address (str): Address of the agent
            lat (float): Latitude of the location
            lon (float): Longitude of the location
            location (str): Location
            min_temp (float): Minimum temperature
            max_temp (float): Maximum temperature
            sends_to (list[SendsTo]): List of destinations where the user wants to receive the temperature alert
            email (Optional[str]): Email of the user

        Returns:
            None

        """
        sends_to = list(set(sends_to))  # remove duplicates from sends_to list
        await self.connect()  # connect to the database
        await self.engine.save(
            Data(
                address=address,
                email=email,
                lat=lat,
                lon=lon,
                location=location,
                minimum_temperature=min_temp,
                maximum_temperature=max_temp,
                sends_to=sends_to,
            )
        )  # insert user into database

    async def remove(self, address: str):
        """
        This function is used to remove a user from the database.

        Args:
            address (str): Address of the agent

        Returns:
            None

        """
        await self.connect()  # connect to the database
        await self.engine.database[Data.__collection__].delete_one({"_id": address})
        # remove user from database
