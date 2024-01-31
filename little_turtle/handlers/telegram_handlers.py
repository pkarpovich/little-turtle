from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as redis

from little_turtle.controlles import StoriesController
from little_turtle.handlers import SchedulerHandler
from little_turtle.handlers.middlewares import context_middleware
from little_turtle.handlers.routers import SystemRouter, AdminCommandsRouter, SetStateRouter
from little_turtle.handlers.routers.callback_query_handler_router import CallbackQueryHandlerRouter
from little_turtle.services import AppConfig, LoggerService, TelegramService, ErrorHandlerService


class TelegramHandlers:
    story_controller: StoriesController
    logger_service: LoggerService
    bot: Bot

    def __init__(
            self,
            config: AppConfig,
            stories_controller: StoriesController,
            logger_service: LoggerService,
            telegram_service: TelegramService,
            error_handler_service: ErrorHandlerService,
    ):
        self.error_handler_service = error_handler_service
        self.story_controller = stories_controller
        self.telegram_service = telegram_service
        self.logger_service = logger_service
        self.config = config

        redis_client = redis.from_url(config.REDIS_URL)
        storage = RedisStorage(redis_client)

        self.bot = Bot(config.TELEGRAM_BOT_TOKEN)

        system_router = SystemRouter(self.bot, self.logger_service, self.config, self.error_handler_service)
        admin_commands = AdminCommandsRouter(
            self.bot,
            self.config,
            self.telegram_service,
            self.story_controller
        )
        callback_query_handler_router = CallbackQueryHandlerRouter(
            self.bot,
            self.story_controller,
            config_service=self.config,
            logger_service=self.logger_service,
            telegram_service=self.telegram_service
        )
        set_state_router = SetStateRouter(self.bot, self.story_controller, self.config)

        self.dp = Dispatcher(storage=storage)
        self.dp.update.outer_middleware()(context_middleware)
        self.dp.include_router(system_router.get_router())
        self.dp.include_router(set_state_router.get_router())
        self.dp.include_router(admin_commands.get_router())
        self.dp.include_router(callback_query_handler_router.get_router())

        self.scheduler_handler = SchedulerHandler(admin_commands.send_morning_message)

    async def run(self):
        self.logger_service.info("Telegram turtle is all set and eager to assist! 🐢📲 Just send a command!")
        self.scheduler_handler.start()
        await self.dp.start_polling(self.bot)
