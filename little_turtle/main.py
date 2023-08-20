import asyncio
import os
import random

from langchain.chat_models import ChatOpenAI

from little_turtle.chains import enrich_run_variables, TurtleStoryChain
from little_turtle.services import AppConfig, TelegramService


async def main():
    config = AppConfig(os.environ)

    telegram_service = TelegramService(config)
    await telegram_service.login()
    messages = await telegram_service.get_messages(config.TURTLE_CHANNEL_ID)
    picked_messages = random.sample(messages, 3)

    llm = ChatOpenAI(model_name=AppConfig.OPENAI_MODEL, openai_api_key=config.OPENAI_API_KEY)
    chain = TurtleStoryChain(
        llm=llm,
    )

    story_variables = enrich_run_variables("27.08.2023", picked_messages)
    response_msg = chain.run(story_variables)
    print(response_msg)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
