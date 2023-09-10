from abc import ABC, abstractmethod

from aiogram import Router, Bot
from aiogram.types import InlineKeyboardMarkup, Message


class BaseRouter(ABC):
    router: Router = None

    def __init__(self, bot: Bot):
        self.bot = bot
        self.router = Router()

    @abstractmethod
    def get_router(self) -> Router:
        pass

    async def send_message(
            self,
            message: str,
            chat_id: int,
            reply_id: int = None,
            silent: bool = True,
            show_typing: bool = False,
            buttons: InlineKeyboardMarkup = None
    ) -> Message:
        if show_typing:
            await self.bot.send_chat_action(chat_id, 'typing')

        return await self.bot.send_message(
            chat_id,
            message,
            reply_to_message_id=reply_id,
            disable_notification=silent,
            reply_markup=buttons
        )
