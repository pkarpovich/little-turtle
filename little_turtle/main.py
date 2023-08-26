import asyncio
import os

from langchain.chat_models import ChatOpenAI

from little_turtle.chains import ImagePromptsGeneratorChain, TurtleStoryChain
from little_turtle.controlles import StoriesController
from little_turtle.database import Database
from little_turtle.handlers import TelegramHandlers
from little_turtle.services import AppConfig
from little_turtle.stores import StoryStore


async def main():
    config = AppConfig(os.environ)
    database = Database(config)

    story_store = StoryStore(database.db)

    llm = ChatOpenAI(model_name=AppConfig.OPENAI_MODEL, openai_api_key=config.OPENAI_API_KEY)
    story_chain = TurtleStoryChain(llm)
    image_prompt_chain = ImagePromptsGeneratorChain(llm)

    stories_controller = StoriesController(
        story_store,
        story_chain,
        image_prompt_chain,
    )

    telegram_handler = TelegramHandlers(config, stories_controller)
    telegram_handler.run()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
