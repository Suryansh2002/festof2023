import asyncio
import os

from motor.motor_asyncio import AsyncIOMotorClient
from odmantic.engine import AIOEngine
from odmantic.field import Field
from odmantic.model import Model

from messages import SendsTo

MONGODB_URL = os.getenv("MONGODB_URL")
assert MONGODB_URL, "Please set the MONGODB_URL environment variable"


class Data(Model):
    address: str = Field(primary_field=True)
    email: str
    lat: float
    lon: float
    location: str
    minimum_temperature: float
    maximum_temperature: float
    sends_to: list[SendsTo] = Field(default=[SendsTo.AGENT])


class Database:
    def __init__(self) -> None:
        self._started = False

    async def connect(self):
        if self._started:
            return
        self.client = AsyncIOMotorClient(
            MONGODB_URL, io_loop=asyncio.get_running_loop()
        )
        self.engine = AIOEngine(self.client, database="temperature_agent")
        self._started = True

    async def find_all(self):
        await self.connect()
        async for data in self.engine.find(Data):
            yield data

    async def insert(
        self,
        address: str,
        email: str,
        lat: float,
        lon: float,
        location: str,
        min_temp: float,
        max_temp: float,
        sends_to: list[SendsTo],
    ):
        sends_to = list(set(sends_to))
        await self.connect()
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
        )

    async def remove(self, address: str):
        await self.connect()
        await self.engine.database[Data.__collection__].delete_one({"_id": address})
