from abc import ABC, abstractmethod

from aiogram import Router, Bot
from aiogram.types import (
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    Message,
    ReactionTypeEmoji,
)


class BaseRouter(ABC):
    router: Router = None

    def __init__(self, bot: Bot):
        self.bot = bot
        self.router = Router()

    @abstractmethod
    def get_router(self) -> Router:
        pass

    async def set_message_reaction(self, chat_id: int, message_id: int, reaction: str):
        await self.bot.set_message_reaction(
            chat_id, message_id, [ReactionTypeEmoji(emoji=reaction)]
        )

    async def send_message(
        self,
        message: str,
        chat_id: int,
        reply_id: int = None,
        silent: bool = True,
        photo_url: str = None,
        show_typing: bool = False,
        buttons: InlineKeyboardMarkup | ReplyKeyboardMarkup = None,
    ) -> Message:
        if show_typing:
            await self.bot.send_chat_action(chat_id, "typing")

        if photo_url is not None:
            return await self.bot.send_photo(
                chat_id,
                photo_url,
                caption=message,
                reply_to_message_id=reply_id,
                disable_notification=silent,
                reply_markup=buttons,
            )

        return await self.bot.send_message(
            chat_id,
            message,
            reply_to_message_id=reply_id,
            disable_notification=silent,
            reply_markup=buttons,
        )
