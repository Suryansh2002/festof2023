# Temperature Alert Agent

**This project was in IIT Bombay's Techfest Competiotion [HackAI]() Zonals.**

## Project Details

**Your challenge is to create the Temperature Alert Agent using [uAgent library](https://fetch.ai/docs), a tool that:**

1. Connects to a free weather API to fetch real-time temperatures for the specified location.

2. Lets users set their preferred temperature range (e.g., a minimum and maximum temperature) and location.

3. Sends an alert/notification to the user when the current temperature in their chosen
   location goes below the minimum or above the maximum threshold they've set

## Setting up the Project

### 1. Prerequisites

- Make sure you have python installed in your system by running `python --version` on your terminal

- Install poetry on your system by running
  ```
  pip install poetry
  ```

### 2. Cloning the Project

- Run the command on your terminal `git clone <repository_url>`

- Replace `<repository_url>` with the actual URL of the project's Git repository.

- Now navigate to the Project Directory by running `cd project_directory`

### 3. Creating a Virtual environment

- Inside the project directory, your should create a virtual environment using Poetry:

  ```
  poetry install
  ```

  This command reads the project's pyproject.toml file and sets up a virtual environment with the required dependencies.

### 4. Generating a MongoDb connection String to use in the .env file (Mentioned in the next point)

- Go to [MongoDb](https://www.mongodb.com/) and create a new account. Answer the basic questions and click on finish

- Choose M0 databse configuration.

- Make a username and password and click on create user

- Add a new IP Address `0.0.0.0/0` and click on create entry

- Click on create and close go the Overview.

- You will be taken to a overview page.

- Now click on Connect and click on drivers and select the driver "Python".

- Copy your connection string and Replace `<password>` with the password for the your account made in one of the above steps.

### 5. Setting up the .env file

- Create an account on [OpenWeatherMap](https://openweathermap.org/) and get an Api Key

- Create a file in the project directory named `.env` and paste the following code in it.

  ```
  WEATHER_API_KEY="<your_api_key_here>"
  TEMPERATURE_SEED="temperature"

  EMAIL_SENDER = "<email_of_sendor>"
  EMAIL_PASSWORD = "<sendor_email_password>"

  MONGODB_URL="<your_connection_string>"
  ```

- Replace `<your_api_key_here>` with your your api key

- Replace `<email_sendor>` with the email you want to send the alert from

- Replace `<sendor_email_password>` with password for the that gmail account to help authenticate the account

  If you don't know how to generate app passwords for your google account refer to this [link](https://support.google.com/accounts/answer/185833?hl=en#zippy=)

- Replace the `<your_connection_string>` with your mongodb connection string you generated in the last point

### 6.Run the main script

```
py src/main.py
```

### 7.Set up the client script

Now that we have set up the integrations, let’s run a client script. To do this, create a new Python file in the project folder called `client.py`, and paste the following:

```py
from dotenv import load_dotenv

load_dotenv()
import os

from uagents import Agent, Context
from uagents.setup import fund_agent_if_low

from src.messages import SendsTo, TemperatureRequest, UAgentResponse, UAgentResponseType

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
        "agent1qfe0vshvrd8jl0xj70da578puz3duut5l0rffp8am9nyq472fwjwv3nj3zg",  # Address of the temperature agent
        TemperatureRequest(
            location="lucknow",
            minimum_temperature=20,
            maximum_temperature=25,
            sends_to=[SendsTo.AGENT],
        ),
    )"""
    #sending email is not needed if sends_to list doesn't have SendsTo.EMAIL
    await ctx.send(
        "agent1qfe0vshvrd8jl0xj70da578puz3duut5l0rffp8am9nyq472fwjwv3nj3zg",
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


if __name__ == "__main__":
    main_agent.run()
```

This Script will send Temperature Request to =
location="lucknow",
minimum_temperature=20,
maximum_temperature=25.

You can edit these fields in the above code as per your choice

### 8.Run the client script

```sh
py client.py
```
