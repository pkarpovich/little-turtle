from datetime import datetime

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

from little_turtle.constants import Reactions, error_messages, messages
from little_turtle.controlles import StoriesController
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.base.base_stories_router import BaseStoriesRouter
from little_turtle.utils import validate_date, parse_date, pretty_print_json


class SetStateRouter(BaseStoriesRouter):
    def __init__(self, bot: Bot, story_controller: StoriesController):
        super().__init__(bot, story_controller)

    def get_router(self) -> Router:
        self.router.message(Command("reset_target_topics"))(self.__reset_target_topics_handler)
        self.router.message(Command("set_image_prompt"))(self.__set_image_prompt_handler)
        self.router.message(Command("add_target_topic"))(self.__add_target_topic_handler)
        self.router.message(Command("suggest_topics"))(self.__suggest_topics_handler)
        self.router.message(Command("set_image"))(self.__set_image_handler)
        self.router.message(Command("set_story"))(self.__set_story_handler)
        self.router.message(Command("set_date"))(self.__set_date_handler)
        self.router.message(Command("cancel"))(self.__cancel_handler)
        self.router.message(Command("state"))(self.__state_handler)

        return self.router

    async def __reset_target_topics_handler(self, msg: Message, ctx: BotContext):
        await ctx.state.update_data(target_topics=list())
        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)

    async def __suggest_topics_handler(self, msg: Message, ctx: BotContext):
        if not await self.__validate_date(msg, msg.chat.id):
            return

        await self.async_generate_action(ctx, self.suggest_target_topics)

    async def __add_target_topic_handler(self, msg: Message, ctx: BotContext):
        if not msg.reply_to_message or not msg.reply_to_message.text:
            await self.send_message(error_messages.ERR_NO_REPLY_STORY_TOPIC, msg.chat.id)
            return

        await self.add_target_topic(msg.reply_to_message.text, ctx)

    async def __set_date_handler(self, msg: Message, ctx: BotContext):
        if not await self.__validate_date(msg, msg.chat.id):
            return

        await ctx.state.update_data(date=msg.reply_to_message.text)
        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)

    async def __set_story_handler(self, msg: Message, ctx: BotContext):
        if not msg.reply_to_message or not msg.reply_to_message.text:
            await self.send_message(error_messages.ERR_NO_REPLY_STORY, msg.chat.id)
            return

        await ctx.state.update_data(story=msg.reply_to_message.text)
        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)

    async def __set_image_prompt_handler(self, msg: Message, ctx: BotContext):
        if not msg.reply_to_message or not msg.reply_to_message.text:
            await self.send_message(error_messages.ERR_NO_REPLY_IMAGE_PROMPT, msg.chat.id)
            return

        await ctx.state.update_data(image_prompt=msg.reply_to_message.text)
        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)

    async def __set_image_handler(self, msg: Message, ctx: BotContext):
        if (
                not msg.reply_to_message
                or not msg.reply_to_message.photo
                or not len(msg.reply_to_message.photo) > 1
        ):
            await self.send_message(error_messages.ERR_NO_REPLY_IMAGE, msg.chat.id)
            return

        await ctx.state.update_data(image=msg.photo[-1].file_id)
        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)

    async def __state_handler(self, _: Message, ctx: BotContext):
        data = await ctx.state.get_data()
        if not data:
            return await self.send_message(messages.NO_STATE, ctx.chat_id)

        await self.send_message(
            pretty_print_json(data),
            ctx.chat_id
        )

    async def __cancel_handler(self, msg: Message, ctx: BotContext):
        await ctx.state.clear()
        await self.set_message_reaction(ctx.chat_id, msg.message_id, Reactions.LIKE)

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
