from __future__ import annotations

import os
from typing import Optional

import aiohttp  # for making http requests

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
assert WEATHER_API_KEY, "Please set the WEATHER_API_KEY environment variable"


class RequestHandler:
    """
    This class is used to handle http requests.

    Attributes:
        _session (Optional[aiohttp.ClientSession]): aiohttp.ClientSession object

    """

    def __init__(self) -> None:
        """
        The constructor for RequestHandler class.

        Returns:
            None

        """
        self._session: Optional[
            aiohttp.ClientSession
        ] = None  # initialize session to None

    async def start(self):
        """
        This function is used to start the session.

        Returns:
            None

        """
        if self._session and not self._session.closed:
            return  # do not proceed if session is already started
        self._session = aiohttp.ClientSession()  # start session

    async def stop(self):
        """
        This function is used to stop the session.

        Returns:
            None

        """
        if self._session is None:
            return  # do not proceed if session is None
        if not self._session.closed:
            await self._session.close()
        self._session = None

    @property
    def session(self):
        """
        This function is used to get the session.

        Returns:
            aiohttp.ClientSession: aiohttp.ClientSession object

        Raises:
            RuntimeError: Session not started

        """
        if self._session is None or self._session.closed:
            raise RuntimeError(
                "Session not started"
            )  # raise exception if session is not started
        return self._session

    async def fetch_lat_and_lon(self, location: str) -> tuple[float, float]:
        """
        This function is used to fetch the latitude and longitude of the location.

        Args:
            location (str): Location to fetch latitude and longitude of

        Returns:
            tuple[float, float]: Latitude and longitude of the location

        Raises:
            ValueError: Location not found

        """
        async with self.session.get(  # make http request to fetch latitude and longitude
            f"http://api.openweathermap.org/geo/1.0/direct?q={location}&appid={WEATHER_API_KEY}"
        ) as response:
            data = await response.json()
            try:
                return data[0]["lat"], data[0]["lon"]  # return latitude and longitude
            except Exception:
                raise ValueError(
                    f"Location: {location} not found"
                )  # raise exception if location is not found

    async def fetch_temperature(self, lat: float, lon: float) -> float:
        """
        This function is used to fetch the temperature of the location.

        Args:
            lat (float): Latitude of the location
            lon (float): Longitude of the location

        Returns:
            float: Temperature of the location

        """
        async with self.session.get(  # make http request to fetch temperature
            f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={WEATHER_API_KEY}&units=metric"
        ) as response:
            data = await response.json()
            return data["main"]["temp"]  # return temperature
