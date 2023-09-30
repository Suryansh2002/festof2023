from __future__ import annotations

import os
from typing import TYPE_CHECKING

import aiohttp
from uagents import Agent
from uagents.setup import fund_agent_if_low

from messages import (SendsTo, TemperatureRequest, UAgentResponse,
                      UAgentResponseType)
from utils.cooldown import Cooldown
from utils.database import Database
from utils.email import send_email, send_verifaction, verify_regex
from utils.requests import RequestHandler

if TYPE_CHECKING:
    from uagents import Context

TEMPERATURE_SEED = os.getenv("TEMPERATURE_SEED")

temperate_agent = Agent(name="temperature", seed=TEMPERATURE_SEED)
fund_agent_if_low(str(temperate_agent.wallet.address()))

request_handler = RequestHandler()
database = Database()
update_cooldown = Cooldown(5 * 60)
alert_cooldown = Cooldown(3 * 60 * 60)


@temperate_agent.on_event("startup")
async def startup(ctx: Context):
    ctx.logger.info("Starting up temperature agent")
    await request_handler.start()


@temperate_agent.on_event("shutdown")
async def shutdown(ctx: Context):
    ctx.logger.info("Shutting down temperature agent")
    await request_handler.stop()


@temperate_agent.on_interval(period=10 * 60)
async def scan_all(ctx: Context):
    async for data in database.find_all():
        if alert_cooldown.on_waiting(data.address):
            continue

        temperature = await request_handler.fetch_temperature(data.lat, data.lon)
        if temperature < data.minimum_temperature:
            body = (
                f"Current Temperature: {temperature}\n"
                f"Temperature lower than the set minimum threshold of {data.minimum_temperature} Celsius\n"
                f"Location: {data.location.title()}\n"
            )
        elif temperature > data.maximum_temperature:
            body = (
                f"Current Temperature: {temperature}\n"
                f"Temperature lower than the set maximum threshold of {data.maximum_temperature} Celsius\n"
                f"Location: {data.location.title()}\n"
            )
        else:
            continue

        if SendsTo.EMAIL in data.sends_to:
            try:
                await send_email(data.email, "TEMPERATURE ALERT !", body)
            except Exception as e:
                ctx.logger.warn(str(e))
        if SendsTo.AGENT in data.sends_to:
            await ctx.send(
                data.address,
                UAgentResponse(type=UAgentResponseType.MESSAGE, message=body),
            )
        alert_cooldown.update(data.address)


@temperate_agent.on_message(model=TemperatureRequest, replies=UAgentResponse)
async def add_user(ctx: Context, sender: str, message: TemperatureRequest):
    if update_cooldown.on_waiting(sender):
        await ctx.send(
            sender,
            UAgentResponse(
                type=UAgentResponseType.ERROR,
                message="You are on cooldown, try again in 5 minutes !",
            ),
        )
        return
    update_cooldown.update(sender)

    ctx.logger.info(f"Received temperature request for location: {message.location}")

    try:
        verify_regex(message.email)
        lat, lon = await request_handler.fetch_lat_and_lon(message.location)
        await send_verifaction(message.email)
    except Exception as e:
        ctx.logger.warn(str(e))
        await ctx.send(
            sender, UAgentResponse(type=UAgentResponseType.ERROR, message=str(e))
        )
        return

    await database.insert(
        address=sender,
        email=message.email,
        lat=lat,
        lon=lon,
        location=message.location,
        min_temp=message.minimum_temperature,
        max_temp=message.maximum_temperature,
        sends_to=message.sends_to,
    )

    await ctx.send(
        sender,
        UAgentResponse(
            type=UAgentResponseType.MESSAGE,
            message="Location added successfully for updates !",
        ),
    )


@temperate_agent.on_message(model=UAgentResponse)
async def remove_user(ctx: Context, sender: str, message: UAgentResponse):
    if message.message != "remove":
        return
    if update_cooldown.on_waiting(sender):
        await ctx.send(
            sender,
            UAgentResponse(
                type=UAgentResponseType.ERROR,
                message="You are on cooldown, try again in 5 minutes !",
            ),
        )
        return
    update_cooldown.update(sender)
    ctx.logger.info(f"Removing user {sender} !")
    await database.remove(sender)
