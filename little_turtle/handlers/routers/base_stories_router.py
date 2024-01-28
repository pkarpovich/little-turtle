from abc import abstractmethod
from os import path
from typing import Optional
from urllib.parse import urlparse

from aiogram import Bot, Router
from aiogram.types import URLInputFile

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
