import os

from dependency_injector import containers, providers
from langchain.chat_models import ChatOpenAI

from little_turtle.chains import (
    TurtleStoryChain,
    StoryReviewerChain,
    StorySummarizationChain,
    ImagePromptsGeneratorChain,
)
from little_turtle.controlles import StoriesController
from little_turtle.database import Database
from little_turtle.handlers import TelegramHandlers
from little_turtle.services import (
    AppConfig,
    ImageGenerationService,
    LoggerService,
    TelegramService,
    ErrorHandlerService
)
from little_turtle.stores import StoryStore


class Container(containers.DeclarativeContainer):
    logger_service = providers.Factory(LoggerService)

    config = providers.Factory(AppConfig, env=os.environ)
    database = providers.Singleton(Database, config=config)

    db = providers.Callable(lambda database: database.db, database=database)

    error_handler_service = providers.Singleton(ErrorHandlerService, config=config, logger_service=logger_service)
    telegram_service = providers.Factory(TelegramService, config=config)
    image_generation_service = providers.Factory(ImageGenerationService, config=config, logger_service=logger_service)

    story_store = providers.Factory(StoryStore, db=db)

    model_name = providers.Callable(lambda config: config.OPENAI_MODEL, config=config)
    openai_api_key = providers.Callable(lambda config: config.OPENAI_API_KEY, config=config)

    llm = providers.Singleton(ChatOpenAI, model_name=model_name, openai_api_key=openai_api_key)

    story_chain = providers.Factory(TurtleStoryChain, llm=llm, config=config)
    story_reviewer_chain = providers.Factory(StoryReviewerChain, llm=llm, config=config)
    image_prompt_chain = providers.Factory(ImagePromptsGeneratorChain, llm=llm, config=config)
    story_summarization_chain = providers.Factory(StorySummarizationChain, llm=llm, config=config)

    stories_controller = providers.Factory(
        StoriesController,
        config=config,
        story_store=story_store,
        story_chain=story_chain,
        image_prompt_chain=image_prompt_chain,
        story_reviewer_chain=story_reviewer_chain,
        image_generation_service=image_generation_service,
        story_summarization_chain=story_summarization_chain,
    )

    telegram_handlers = providers.Factory(
        TelegramHandlers,
        config=config,
        error_handler_service=error_handler_service,
        stories_controller=stories_controller,
        telegram_service=telegram_service,
        logger_service=logger_service,
    )
