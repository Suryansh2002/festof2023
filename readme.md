# Temperature Alert Agent

**This project was sent for IIT Bombay's Techfest Competition [HackAI](https://techfest.org/competitions/hack-aI) Zonals.**

## Project Details

**Your challenge is to create the Temperature Alert Agent using [uAgent library](https://fetch.ai/docs), a tool that:**

1. Connects to a free weather API to fetch real-time temperatures for the specified location.

2. Lets users set their preferred temperature range (e.g., a minimum and maximum temperature) and location.

3. Sends an alert/notification to the user when the current temperature in their chosen
   location goes below the minimum or above the maximum threshold they've set

## Setting up the Project

### Step 1. Prerequisites

- Make sure you have python installed in your system by running `python --version` on your terminal

- Install poetry on your system by running
  ```
  pip install poetry
  ```

### Step 2. Cloning the Project

- Run the command on your terminal `git clone <repository_url>`

- Replace `<repository_url>` with the actual URL of the project's Git repository.

- Now navigate to the Project Directory by running `cd project_directory`

### Step 3. Creating a Virtual environment

- Inside the project directory, your should create a virtual environment using Poetry:

  ```
  poetry install
  ```

  This command reads the project's pyproject.toml file and sets up a virtual environment with the required dependencies.

- Now activate the poetry shell using the following command.

  ```
  poetry shell
  ```

### Step 4. Generating a MongoDb connection String to use in the .env file (Mentioned in the next point)

- Go to [MongoDb](https://www.mongodb.com/) and create a new account. Answer the basic questions and click on finish

- Choose M0 databse configuration.

- Make a username and password and click on create user

- Add a new IP Address `0.0.0.0/0` and click on create entry

- Click on create and close go the Overview.

- You will be taken to a overview page.

- Now click on Connect and click on drivers and select the driver "Python".

- Copy your connection string and Replace `<password>` with the password for the your account made in one of the above steps.

### Step 5. Setting up the .env file

- Create an account on [OpenWeatherMap](https://openweathermap.org/) and get an Api Key

- Create a file in the project directory named `.env` and paste the following code in it.

  ```
  WEATHER_API_KEY="<your_api_key_here>"
  TEMPERATURE_SEED="<your_seed_here>"

  EMAIL_SENDER = "<email_of_sendor>"
  EMAIL_PASSWORD = "<sendor_email_password>"

  MONGODB_URL="<your_connection_string>"
  ```

- Replace `<your_api_key_here>` with your your api key

- Replace `<email_sendor>` with the email you want to send the alert from

- Replace `<sendor_email_password>` with password for the that gmail account to help authenticate the account

  If you don't know how to generate app passwords for your google account refer to this [link](https://support.google.com/accounts/answer/185833?hl=en#zippy=)

- Replace `<your_seed_here>` with a name of choice.

  Example - `TEMPERATURE_SEED="temperature"`

- Replace the `<your_connection_string>` with your mongodb connection string you generated in the last point

### Step 6. Run the main script

```
py src/main.py
```

Copy the Temperature agent address printed in the console.We are going to need it in step 7.

### Step 7.Set up the client script

Now that we have set up the integrations, let’s run a client script. To do this, create a new Python file in the project folder called `client.py`, and paste the following:

```py
from dotenv import load_dotenv

load_dotenv()
import os

from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from src.messages import (
    SendsTo,
    TemperatureCondition,
    TemperatureRequest,
    TemperatureWarn,
    UAgentResponse,
    UAgentResponseType,
)

MAIN_AGENT_SEED = os.getenv("MAIN_AGENT_SEED")


main_agent = Agent(
    name="main_agent",
    port=8001,
    seed=MAIN_AGENT_SEED,
    endpoint=["http://localhost:8001/submit"],
)

fund_agent_if_low(str(main_agent.wallet.address()))


@main_agent.on_interval(period=5)
async def send_temperature_request(ctx: Context):
    """await ctx.send(
        "<temperaure_agent_address>",  # Address of the temperature agent
        TemperatureRequest(
            location="lucknow",
            minimum_temperature=20,
            maximum_temperature=25,
            sends_to=[SendsTo.AGENT],
        ),
    )"""
    # passing email is not needed if sends_to list doesn't have SendsTo.EMAIL
    await ctx.send(
        "<temperaure_agent_address>",
        TemperatureRequest(
            location="lucknow",
            email="yourmail@gmail.com",
            minimum_temperature=20,
            maximum_temperature=25,
            sends_to=[SendsTo.EMAIL, SendsTo.AGENT],
        ),
    )
    # if sends_to list contains SendsTo.EMAIL, then passing email is mandatory."""


@main_agent.on_message(model=UAgentResponse)
async def receive_update(ctx: Context, _: str, message: UAgentResponse):
    if message.type == UAgentResponseType.MESSAGE:
        ctx.logger.info(str(message.message))
    elif message.type == UAgentResponseType.ERROR:
        ctx.logger.error(str(message.message))


@main_agent.on_message(model=TemperatureWarn)
async def receive_warning(ctx: Context, _: str, message: TemperatureWarn):
    # Client can do anything with the data received

    thershold = {
        TemperatureCondition.LOW: message.minimum_temperature,
        TemperatureCondition.HIGH: message.maximum_temperature,
    }
    ctx.logger.info(
        f"Temperature at {message.location} is {message.temperature}\n"
        f"{message.condition.value.title()}er than the set threshold of {thershold[message.condition]}!"
    )


if __name__ == "__main__":
    main_agent.run()
```

This Script will send Temperature Request to the data listed below.

Make sure to replace the `yourmail@gmail.com` to receive alert mails.

Replace the `<temperaure_agent_address>` with the address copied in step 6.

You can edit other fields as per your choice fields in the above code.

This snippet is the part of the above code to help demonstrate better.

```py
    await ctx.send(
        "<temperaure_agent_address>",
        TemperatureRequest(
            location="lucknow",
            email="yourmail@gmail.com",
            minimum_temperature=20,
            maximum_temperature=25,
            sends_to=[SendsTo.EMAIL, SendsTo.AGENT],
        ),
    )
```

### Step 8.Run the client script

```sh
py client.py
```
