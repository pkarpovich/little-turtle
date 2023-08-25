import asyncio
import os

from langchain.chat_models import ChatOpenAI

from little_turtle.chains import ImagePromptsGeneratorChain, TurtleStoryChain
from little_turtle.database import Database
from little_turtle.services import AppConfig, TelegramService
from little_turtle.stores import StoryStore


async def main():
    config = AppConfig(os.environ)
    database = Database(config)

    story_store = StoryStore(database.db)

    telegram_service = TelegramService(config)
    await telegram_service.login()

    messages = story_store.get_all(
        query={
            "image_prompt": {
                "$ne": ""
            }
        }
    )

    # messages = await telegram_service.get_messages(config.TURTLE_CHANNEL_ID)

    # for message in messages:
    #     story_store.create(
    #         Story(
    #             content=message,
    #             image_prompt='',
    #         )
    #     )

    llm = ChatOpenAI(model_name=AppConfig.OPENAI_MODEL, openai_api_key=config.OPENAI_API_KEY)
    story_chain = TurtleStoryChain(
        llm=llm,
    )

    story_variables = TurtleStoryChain.enrich_run_variables("27.08.2023", messages)
    new_story = story_chain.run(story_variables)

    image_prompt_chain = ImagePromptsGeneratorChain(
        llm=llm,

    )
    image_prompt_variables = ImagePromptsGeneratorChain.enrich_run_variables(new_story, messages)
    image_prompt = image_prompt_chain.run(image_prompt_variables)

    new_story["image_prompt"] = image_prompt

    print(image_prompt)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
