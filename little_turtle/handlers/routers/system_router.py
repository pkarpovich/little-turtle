from aiogram import Router, Bot
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, ErrorEvent

from little_turtle.constants import error_messages, messages
from little_turtle.services import LoggerService, AppConfig, ErrorHandlerService
from .base_router import BaseRouter


class SystemRouter(BaseRouter):
    def __init__(
            self, bot: Bot,
            logger_service: LoggerService,
            config_service: AppConfig,
            error_handler_service: ErrorHandlerService
    ):
        super().__init__(bot)
        self.logger_service = logger_service
        self.config_service = config_service
        self.error_handler_service = error_handler_service

    def get_router(self) -> Router:
        self.router.message(
            lambda message: message.from_user.id not in self.config_service.TELEGRAM_ALLOWED_USERS
        )(self.handle_disallowed_users)
        self.router.message(CommandStart())(self.start_handler)
        self.router.message(Command("ping"))(self.handle_ping)
        self.router.error()(self.error_handler)

        return self.router

    async def handle_disallowed_users(self, message: Message):
        self.logger_service.info(
            "Disallowed user tried to use the bot",
            user_id=message.from_user.id,
            user_message=message
        )

        await self.send_message(error_messages.ERR_UNKNOWN_USER, message.chat.id)

    async def error_handler(self, event: ErrorEvent):
        self.logger_service.info("Error while handling update", exc_info=event.exception)
        self.error_handler_service.capture_exception(event.exception)

        if event.update.callback_query is not None:
            chat_id = event.update.callback_query.message.chat.id
        elif event.update.message is not None:
            chat_id = event.update.message.chat.id
        else:
            return

        await self.send_message(error_messages.UNHANDLED_ERROR, chat_id)

    async def start_handler(self, message: Message):
        await self.send_message(messages.START_REPLY, message.chat.id)

    async def handle_ping(self, message: Message):
        await self.send_message(messages.PONG_REPLY, message.chat.id)
