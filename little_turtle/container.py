import os

from dependency_injector import containers, providers

from little_turtle.llm_provider import LLMProvider, ProviderType
from little_turtle.chains import (
    TurtleStoryChain,
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
from little_turtle.prompts.prompts_provider import PromptsProvider
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

    
    llm_provider = providers.Singleton(LLMProvider, config=config)
    
    openai_client = providers.Factory(
        lambda provider: provider.build(ProviderType.OPENAI),
        provider=llm_provider
    )
    
    anthropic_client = providers.Factory(
        lambda provider: provider.build(ProviderType.ANTHROPIC),
        provider=llm_provider
    )
    
    prompts_provider = providers.Singleton(PromptsProvider)


    story_chain = providers.Factory(
        TurtleStoryChain, llm_client=openai_client, prompts_provider=prompts_provider
    )
    historical_events_chain = providers.Factory(
        HistoricalEventsChain, 
        llm_client=anthropic_client,
        prompts_provider=prompts_provider
    )
    image_generator_chain = providers.Factory(
        ImageGeneratorChain, llm_client=openai_client, prompts_provider=prompts_provider
    )

    stories_controller = providers.Factory(
        StoriesController,
        config=config,
        story_chain=story_chain,
        telegram_service=telegram_service,
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
