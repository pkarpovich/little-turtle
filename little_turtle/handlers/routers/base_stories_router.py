from abc import abstractmethod
from os import path
from typing import Optional, Callable
from urllib.parse import urlparse

from aiogram import Bot, Router
from aiogram.types import URLInputFile

from little_turtle.constants import Stickers, Reactions
from little_turtle.controlles import StoriesController
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.base_router import BaseRouter
from little_turtle.handlers.routers.callback_data import ForwardCallback, ForwardAction
from little_turtle.utils import prepare_buttons


class BaseStoriesRouter(BaseRouter):
    def __init__(self, bot: Bot, story_controller: StoriesController):
        super().__init__(bot)

        self.story_controller = story_controller

    @abstractmethod
    def get_router(self) -> Router:
        pass

    async def suggest_target_topics(self, ctx: BotContext) -> [str]:
        topics = self.story_controller.suggest_on_this_day_events(ctx.message.reply_to_message.text)
        await self.send_message(
            topics,
            ctx.chat_id,
            buttons=prepare_buttons(
                dict([
                    ('1', ForwardCallback(action=ForwardAction.SELECT_TARGET_TOPIC, payload="1")),
                    ('2', ForwardCallback(action=ForwardAction.SELECT_TARGET_TOPIC, payload="2")),
                    ('3', ForwardCallback(action=ForwardAction.SELECT_TARGET_TOPIC, payload="3")),
                    ('4', ForwardCallback(action=ForwardAction.SELECT_TARGET_TOPIC, payload="4")),
                    ('5', ForwardCallback(action=ForwardAction.SELECT_TARGET_TOPIC, payload="5")),
                ])
            )
        )

        return topics.split('\n\n')

    async def generate_story(self, ctx: BotContext) -> Optional[str]:
        data = await ctx.state.get_data()
        date = data.get('date')
        target_topics = data.get('target_topics', list())

        story = self.story_controller.suggest_story(date, target_topics)
        await self.send_message(
            story,
            chat_id=ctx.chat_id,
            buttons=prepare_buttons(
                {
                    '👎': ForwardCallback(action=ForwardAction.REGENERATE_STORY),
                    '👍': ForwardCallback(action=ForwardAction.SET_STORY),
                }
            )
        )

        return story

    async def generate_image_prompt(self, ctx: BotContext) -> Optional[str]:
        text = (await ctx.state.get_data()).get('story')

        image_prompt = self.story_controller.suggest_story_prompt(text)
        await self.send_message(
            image_prompt,
            chat_id=ctx.chat_id,
            buttons=prepare_buttons(
                {
                    '👎': ForwardCallback(action=ForwardAction.REGENERATE_IMAGE_PROMPT),
                    '👍': ForwardCallback(action=ForwardAction.SET_IMAGE_PROMPT),
                }
            )
        )

        return image_prompt

    async def generate_image(self, ctx: BotContext):
        image_prompt = (await ctx.state.get_data()).get('image_prompt')
        image_url = self.story_controller.imagine_story(image_prompt)

        image = URLInputFile(image_url, filename=path.basename(urlparse(image_url).path))
        return await self.bot.send_photo(
            ctx.chat_id,
            image,
            reply_markup=prepare_buttons(
                {
                    '👎': ForwardCallback(action=ForwardAction.REGENERATE_IMAGE),
                    '👍': ForwardCallback(action=ForwardAction.SET_IMAGE),
                }
            )
        )

    async def add_target_topic(self, topic, ctx: BotContext):
        data = await ctx.state.get_data()

        target_topics: [str] = data.get('target_topics') or list()
        target_topics.append(topic)

        await ctx.state.update_data(target_topics=target_topics)
        await self.set_message_reaction(ctx.message.chat.id, ctx.message.message_id, Reactions.LIKE)

    async def async_generate_action(self, ctx: BotContext, action: Callable):
        msg = await self.bot.send_sticker(ctx.chat_id, Stickers.WIP)
        await action(ctx)
        await self.bot.delete_message(ctx.chat_id, msg.message_id)
