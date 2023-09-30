from __future__ import annotations

import os
from typing import Optional

import aiohttp

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
assert WEATHER_API_KEY, "Please set the WEATHER_API_KEY environment variable"


class RequestHandler:
    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None

    async def start(self):
        if self._session and not self._session.closed:
            return
        self._session = aiohttp.ClientSession()

    async def stop(self):
        if self._session:
            await self._session.close()
        self._session = None

    @property
    def session(self):
        if self._session is None:
            raise RuntimeError("Session not started")
        return self._session

    async def fetch_lat_and_lon(self, location: str) -> tuple[float, float]:
        async with self.session.get(
            f"http://api.openweathermap.org/geo/1.0/direct?q={location}&appid={WEATHER_API_KEY}"
        ) as response:
            data = await response.json()
            try:
                return data[0]["lat"], data[0]["lon"]
            except IndexError:
                raise ValueError(f"Location: {location} not found")

    async def fetch_temperature(self, lat: float, lon: float) -> float:
        async with self.session.get(
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        ) as response:
            data = await response.json()
            return data["main"]["temp"]
