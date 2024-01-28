from datetime import datetime

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from little_turtle.constants import Reactions, error_messages
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.base_router import BaseRouter
from little_turtle.utils import validate_date, parse_date


class SetStateRouter(BaseRouter):
    def __init__(self, bot: Bot):
        super().__init__(bot)

    def get_router(self) -> Router:
        self.router.message(Command("set_image_prompt"))(self.__set_image_prompt_handler)
        self.router.message(Command("set_image"))(self.__set_image_handler)
        self.router.message(Command("set_story"))(self.__set_story_handler)
        self.router.message(Command("set_date"))(self.__set_date_handler)

        return self.router

    async def __set_date_handler(self, msg: Message, ctx: BotContext):
        if not await self.__validate_date(msg, msg.chat.id):
            return

        await ctx.state.update_data(date=msg.reply_to_message.text)
        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)

    async def __set_story_handler(self, msg: Message, ctx: BotContext):
        await ctx.state.update_data(story=msg.reply_to_message.text)
        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)

    async def __set_image_prompt_handler(self, msg: Message, ctx: BotContext):
        await ctx.state.update_data(image_prompt=msg.reply_to_message.text)
        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)

    async def __set_image_handler(self, msg: Message, ctx: BotContext):
        await ctx.state.update_data(image=msg.photo[-1].file_id)
        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)

    async def __validate_date(self, message: Message, chat_id: int) -> bool:
        if not message.reply_to_message or not message.reply_to_message.text:
            await self.send_message(error_messages.ERR_NO_REPLY_DATE, chat_id)
            return False

        if not validate_date(message.reply_to_message.text):
            await self.send_message(error_messages.ERR_INVALID_INPUT_DATE, chat_id)
            return False

        date = parse_date(message.reply_to_message.text)
        if date < datetime.now():
            await self.send_message(error_messages.ERR_DATE_IN_THE_PAST, chat_id)
            return False

        return True
