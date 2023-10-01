from __future__ import annotations  # for type hinting

import os
from typing import TYPE_CHECKING

from uagents import Agent
from uagents.setup import fund_agent_if_low

from messages import SendsTo, TemperatureRequest, UAgentResponse, UAgentResponseType
from utils.cooldown import Cooldown
from utils.database import Database
from utils.email import send_email, send_verifaction, verify_regex
from utils.requests import RequestHandler

if TYPE_CHECKING:  # to avoid useless imports
    from uagents import Context

TEMPERATURE_SEED = os.getenv("TEMPERATURE_SEED")  # get seed from .env file

temperate_agent = Agent(name="temperature", seed=TEMPERATURE_SEED)  # create agent
fund_agent_if_low(str(temperate_agent.wallet.address()))


# creating instances of classes
request_handler = RequestHandler()
database = Database()

# creating cooldowns
update_cooldown = Cooldown(5 * 60)
alert_cooldown = Cooldown(3 * 60 * 60)


@temperate_agent.on_event("startup")
async def startup(ctx: Context):
    """
    This function is called when the agent starts up.
    It is used to start the database connection and request handler.

    Args:
        ctx (Context): Context object

    Returns:
        None
    """
    ctx.logger.info("Starting up temperature agent")
    await request_handler.start()


@temperate_agent.on_event("shutdown")
async def shutdown(ctx: Context):
    """
    This function is called when the agent shuts down.
    It is used to stop the database connection and request handler.

    Args:
        ctx (Context): Context object

    Returns:
        None
    """
    ctx.logger.info("Shutting down temperature agent")
    await request_handler.stop()


@temperate_agent.on_interval(period=30 * 60)
async def scan_all(ctx: Context):
    """
    This function is called every 30 minutes.
    It is used to scan all the users in the database and send them alerts if required.

    Args:
        ctx (Context): Context object

    Returns:
        None
    """
    async for data in database.find_all():  # fetch all users from database
        if alert_cooldown.on_waiting(data.address):  # check if user is on cooldown
            continue  # if user is on cooldown, skip this user

        # fetch temperature from openweathermap api
        temperature = await request_handler.fetch_temperature(data.lat, data.lon)

        # check if temperature is out of range
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

        # send alerts
        if (
            SendsTo.EMAIL in data.sends_to
        ) and data.email:  # check if user wants to receive email alerts
            try:
                await send_email(data.email, "TEMPERATURE ALERT !", body)
            except Exception as e:
                ctx.logger.error(str(e))
        if (
            SendsTo.AGENT in data.sends_to
        ):  # check if user wants to receive agent alerts
            await ctx.send(
                data.address,
                UAgentResponse(type=UAgentResponseType.MESSAGE, message=body),
            )
        alert_cooldown.update(data.address)  # update cooldown


@temperate_agent.on_message(model=TemperatureRequest, replies=UAgentResponse)
async def add_user(ctx: Context, sender: str, message: TemperatureRequest):
    """ "
    This function is called when a user sends a TemperatureRequest message to the agent.
    It is used to add the user to the database and send a verification email if required.

    Args:
        ctx (Context): Context object
        sender (str): Address of the sender
        message (TemperatureRequest): TemperatureRequest message sent by the user

    Returns:
        None
    """

    # check if user is on cooldown
    if update_cooldown.on_waiting(sender):
        await ctx.send(
            sender,
            UAgentResponse(
                type=UAgentResponseType.ERROR,
                message="You are on cooldown, try again in 5 minutes !",
            ),
        )
        return
    update_cooldown.update(sender)  # update cooldown

    ctx.logger.info(f"Received temperature request for location: {message.location}")

    try:  # fetch lat and lon from openweathermap api
        lat, lon = await request_handler.fetch_lat_and_lon(message.location)
        if (
            SendsTo.EMAIL in message.sends_to
        ):  # check if user wants to receive email alerts
            if message.email is None:  # check if email is provided
                raise Exception("Email is required for email alerts !")

            verify_regex(message.email)  # check if email has viable regex
            await send_verifaction(message.email)

    except Exception as e:  # catch exception if any error occurs
        ctx.logger.error(str(e))
        await ctx.send(
            sender, UAgentResponse(type=UAgentResponseType.ERROR, message=str(e))
        )
        return

    # add user to database
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

    # send success message
    await ctx.send(
        sender,
        UAgentResponse(
            type=UAgentResponseType.MESSAGE,
            message="Location added successfully for updates !",
        ),
    )


@temperate_agent.on_message(model=UAgentResponse, replies=UAgentResponse)
async def remove_user(ctx: Context, sender: str, message: UAgentResponse):
    """
    This function is called when a user sends a UAgentResponse message to the agent.
    It is used to remove the user from the database.

    Args:
        ctx (Context): Context object
        sender (str): Address of the sender
        message (UAgentResponse): UAgentResponse message sent by the user

    Returns:
        None
    """

    if message.message != "remove":
        return  # if message is not "remove", return

    # check if user is on cooldown
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
    await database.remove(sender)  # remove user from database
    await ctx.send(
        sender,
        UAgentResponse(
            type=UAgentResponseType.MESSAGE,
            message="Temperature updates removed successfully !",
        ),
    )  # send success message
