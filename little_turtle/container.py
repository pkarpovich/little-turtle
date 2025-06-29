import os

from dependency_injector import containers, providers
from langchain_openai import ChatOpenAI

from little_turtle.chains import (
    TurtleStoryChain,
    ImagePromptsGeneratorChain,
    ChainAnalytics,
    HistoricalEventsChain,
    ImageGeneratorChain,
)
from little_turtle.controlles import StoriesController
from little_turtle.handlers import TelegramHandlers
from little_turtle.handlers.routers import (
    SystemRouter,
    AdminCommandsRouter,
    SetStateRouter,
)
from little_turtle.handlers.routers.callback_query_handler_router import (
    CallbackQueryHandlerRouter,
)
from little_turtle.services import (
    AppConfig,
    LoggerService,
    TelegramService,
    ErrorHandlerService,
)


class Container(containers.DeclarativeContainer):
    logger_service = providers.Factory(LoggerService)

    config = providers.Factory(AppConfig, env=os.environ)

    error_handler_service = providers.Singleton(
        ErrorHandlerService, config=config, logger_service=logger_service
    )
    telegram_service = providers.Singleton(TelegramService, config=config)

    model_name = providers.Callable(lambda config: config.OPENAI_MODEL, config=config)
    openai_api_key = providers.Callable(
        lambda config: config.OPENAI_API_KEY, config=config
    )

    llm = providers.Singleton(
        ChatOpenAI, model_name=model_name, openai_api_key=openai_api_key
    )

    chain_analytics = providers.Factory(ChainAnalytics, config=config)

    story_chain = providers.Factory(
        TurtleStoryChain, llm=llm, chain_analytics=chain_analytics, config=config
    )
    image_prompt_chain = providers.Factory(
        ImagePromptsGeneratorChain,
        llm=llm,
        config=config,
        chain_analytics=chain_analytics,
    )
    historical_events_chain = providers.Factory(HistoricalEventsChain, config=config)
    image_generator_chain = providers.Factory(ImageGeneratorChain)

    stories_controller = providers.Factory(
        StoriesController,
        config=config,
        story_chain=story_chain,
        telegram_service=telegram_service,
        image_prompt_chain=image_prompt_chain,
        image_generator_chain=image_generator_chain,
        historical_events_chain=historical_events_chain,
    )

    telegram_handlers = providers.Factory(
        TelegramHandlers,
        config=config,
        logger_service=logger_service,
    )
    bot = providers.Callable(
        lambda telegram_handlers: telegram_handlers.bot,
        telegram_handlers=telegram_handlers,
    )

    system_router = providers.Factory(
        SystemRouter,
        bot=bot,
        config_service=config,
        logger_service=logger_service,
        error_handler_service=error_handler_service,
    )
    admin_commands_router = providers.Factory(
        AdminCommandsRouter,
        bot=bot,
        config_service=config,
        telegram_service=telegram_service,
        story_controller=stories_controller,
    )
    callback_query_handler_router = providers.Factory(
        CallbackQueryHandlerRouter,
        bot=bot,
        config_service=config,
        logger_service=logger_service,
        telegram_service=telegram_service,
        story_controller=stories_controller,
    )
    set_state_router = providers.Factory(
        SetStateRouter,
        bot=bot,
        config_service=config,
        story_controller=stories_controller,
    )
