from __future__ import annotations

from dotenv import load_dotenv

load_dotenv()

from uagents import Bureau

from agents import temperate_agent

print(temperate_agent.address)


# initialize bureau
if __name__ == "__main__":
    bureau = Bureau(endpoint=["http://localhost:8000/submit"], port=8000)
    bureau.add(temperate_agent)
    bureau.run()
