from typing import Callable

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery

from little_turtle.constants import Stickers, Reactions
from little_turtle.controlles import StoriesController
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.base_stories_router import BaseStoriesRouter
from little_turtle.handlers.routers.callback_data import ForwardAction, ForwardCallback


class CallbackQueryHandlerRouter(BaseStoriesRouter):
    def __init__(self, bot: Bot, story_controller: StoriesController):
        super().__init__(bot, story_controller)

    def get_router(self) -> Router:
        regenerate_filter = (
                F.action == ForwardAction.REGENERATE_IMAGE_PROMPT
                or F.action == ForwardAction.REGENERATE_STORY
                or F.action == ForwardAction.REGENERATE_IMAGE
        )
        self.router.callback_query(ForwardCallback.filter(regenerate_filter))(self.regenerate_query_handler)

        set_filter = (
                F.action == ForwardAction.SET_DATE
                or F.action == ForwardAction.SET_STORY
                or F.action == ForwardAction.SET_IMAGE_PROMPT
                or F.action == ForwardAction.SET_IMAGE
        )
        self.router.callback_query(ForwardCallback.filter(set_filter))(self.set_query_handler)

        return self.router

    async def regenerate_query_handler(
            self,
            query: CallbackQuery,
            callback_data: ForwardCallback,
            ctx: BotContext
    ):
        msg = query.message

        match callback_data.action:
            case ForwardAction.REGENERATE_STORY:
                await self.__async_generate_action(ctx, self.generate_story)

            case ForwardAction.REGENERATE_IMAGE_PROMPT:
                await self.__async_generate_action(ctx, self.generate_image_prompt)

            case ForwardAction.REGENERATE_IMAGE:
                await self.__async_generate_action(ctx, self.generate_image)

        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.SALUTE_FACE)
        await query.answer("Done!")

    async def set_query_handler(
            self,
            query: CallbackQuery,
            callback_data: ForwardCallback,
            ctx: BotContext
    ):
        msg = query.message

        match callback_data.action:
            case ForwardAction.SET_DATE:
                await ctx.state.update_data(date=msg.text)

            case ForwardAction.SET_STORY:
                await ctx.state.update_data(story=msg.text)

            case ForwardAction.SET_IMAGE_PROMPT:
                await ctx.state.update_data(image_prompt=msg.text)

            case ForwardAction.SET_IMAGE:
                await ctx.state.update_data(image=msg.photo[-1].file_id)

        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)
        await query.answer("Done!")

    async def __async_generate_action(self, ctx: BotContext, action: Callable):
        msg = await self.bot.send_sticker(ctx.chat_id, Stickers.WIP)
        await action(ctx)
        await self.bot.delete_message(ctx.chat_id, msg.message_id)
