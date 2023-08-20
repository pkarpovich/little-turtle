import asyncio
import os

from langchain.chat_models.openai import ChatOpenAI

from little_turtle.chains import TurtleStoryChain
from little_turtle.services.config_service import AppConfig


async def main():
    AppConfig(os.environ)

    chain = TurtleStoryChain(
        llm=ChatOpenAI(),
    )

    response = chain.run({"date": "27.08.2023"})
    print(response)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
