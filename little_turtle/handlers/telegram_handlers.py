from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis import asyncio as redis

from little_turtle.controlles import StoriesController
from little_turtle.handlers import SchedulerHandler
from little_turtle.handlers.middlewares import context_middleware
from little_turtle.handlers.routers import (
    SystemRouter,
    AdminCommandsRouter,
    SetStateRouter,
    CallbackQueryHandlerRouter,
)
from little_turtle.app_config import AppConfig
from little_turtle.services import LoggerService


class TelegramHandlers:
    story_controller: StoriesController
    logger_service: LoggerService
    bot: Bot

    def __init__(self, config: AppConfig, logger_service: LoggerService):
        self.logger_service = logger_service

        self.bot = Bot(config.TELEGRAM_BOT_TOKEN)
        self.scheduler_handler = None

        self.dp = Dispatcher(storage=RedisStorage(redis.from_url(config.REDIS_URL)))
        self.dp.update.outer_middleware()(context_middleware)

    def init_routers(
        self,
        system_router: SystemRouter,
        set_state_router: SetStateRouter,
        admin_commands_router: AdminCommandsRouter,
        callback_query_handler_router: CallbackQueryHandlerRouter,
    ):
        self.dp.include_router(system_router.get_router())
        self.dp.include_router(set_state_router.get_router())
        self.dp.include_router(admin_commands_router.get_router())
        self.dp.include_router(callback_query_handler_router.get_router())
        self.scheduler_handler = SchedulerHandler(
            admin_commands_router.send_morning_message
        )

    async def run(self):
        self.logger_service.info(
            "Telegram turtle is all set and eager to assist! 🐢📲 Just send a command!"
        )
        self.scheduler_handler.start()
        await self.dp.start_polling(self.bot)
