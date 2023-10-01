from dotenv import load_dotenv

load_dotenv()  # loads environment variables from .env file

from uagents import Bureau

from agents import temperate_agent

# initialize bureau and add agents to it
if __name__ == "__main__":
    bureau = Bureau(endpoint=["http://localhost:8000/submit"], port=8000)
    bureau.add(temperate_agent)
    print("Address for temperature Agent: ", temperate_agent.address)
    bureau.run()
