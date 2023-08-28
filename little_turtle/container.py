import os

from dependency_injector import containers, providers
from langchain.chat_models import ChatOpenAI

from little_turtle.chains import TurtleStoryChain, ImagePromptsGeneratorChain
from little_turtle.controlles import StoriesController
from little_turtle.database import Database
from little_turtle.handlers import TelegramHandlers
from little_turtle.services import AppConfig, ImageGenerationService, LoggerService
from little_turtle.stores import StoryStore, HistoryStore


class Container(containers.DeclarativeContainer):
    logger_service = providers.Factory(LoggerService)

    config = providers.Factory(AppConfig, env=os.environ)
    database = providers.Singleton(Database, config=config)

    db = providers.Callable(lambda database: database.db, database=database)

    image_generation_service = providers.Factory(ImageGenerationService, config=config, logger_service=logger_service)
    story_store = providers.Factory(StoryStore, db=db)
    history_store = providers.Factory(HistoryStore, db=db)

    model_name = providers.Callable(lambda config: config.OPENAI_MODEL, config=config)
    openai_api_key = providers.Callable(lambda config: config.OPENAI_API_KEY, config=config)

    llm = providers.Singleton(ChatOpenAI, model_name=model_name, openai_api_key=openai_api_key)

    story_chain = providers.Factory(TurtleStoryChain, llm=llm, config=config)
    image_prompt_chain = providers.Factory(ImagePromptsGeneratorChain, llm=llm, config=config)

    stories_controller = providers.Factory(
        StoriesController,
        story_store=story_store,
        story_chain=story_chain,
        image_prompt_chain=image_prompt_chain,
        image_generation_service=image_generation_service,
    )

    telegram_handlers = providers.Factory(
        TelegramHandlers,
        config=config,
        stories_controller=stories_controller,
        history_store=history_store,
        logger_service=logger_service,
    )
