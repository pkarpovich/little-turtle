from abc import abstractmethod
from os import path
from typing import Optional, Callable
from urllib.parse import urlparse

from aiogram import Bot, Router
from aiogram.types import URLInputFile, BufferedInputFile

from little_turtle.constants import Stickers, error_messages
from little_turtle.controlles import StoriesController
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.actions import ForwardCallback, ForwardAction
from little_turtle.handlers.routers.base.base_router import BaseRouter
from little_turtle.services import AppConfig
from little_turtle.utils import prepare_buttons, validate_date, read_file_from_disk, get_image_path


class BaseStoriesRouter(BaseRouter):
    def __init__(self, bot: Bot, story_controller: StoriesController, config_service: AppConfig):
        super().__init__(bot)

        self.story_controller = story_controller
        self.config = config_service

    @abstractmethod
    def get_router(self) -> Router:
        pass

    async def suggest_target_topics(self, ctx: BotContext) -> [str]:
        data = await ctx.state.get_data()
        date = data.get('date')

        topics_str = self.story_controller.suggest_on_this_day_events(date or ctx.message.reply_to_message.text)
        topics = topics_str.split('\n\n')

        buttons = {
            str(i + 1): ForwardCallback(action=ForwardAction.SELECT_TARGET_TOPIC, payload=str(i + 1))
            for i, _ in enumerate(topics[:5])
        }

        await self.send_message(
            topics_str,
            ctx.chat_id,
            buttons=prepare_buttons(buttons)
        )

        return topics

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

    @staticmethod
    async def add_target_topic(topic, ctx: BotContext):
        data = await ctx.state.get_data()

        target_topics: [str] = data.get('target_topics') or list()
        target_topics.append(topic)

        await ctx.state.update_data(target_topics=target_topics)

    async def preview_story(self, ctx: BotContext):
        data = await ctx.state.get_data()
        if not data:
            return await self.send_message(error_messages.ERR_NO_PREVIEW_DATA, ctx.chat_id)

        date = data.get('date')
        if not date or not validate_date(date):
            return await self.send_message(error_messages.ERR_INVALID_INPUT_DATE, ctx.chat_id)

        photo_path = data.get('image')
        if not photo_path:
            return await self.send_message(error_messages.ERR_NO_STORY_PHOTO, ctx.chat_id)

        photo = read_file_from_disk(photo_path)
        if not photo:
            return await self.send_message(error_messages.ERR_INVALID_PHOTO, ctx.chat_id)

        story = data.get('story')
        if not story:
            return await self.send_message(error_messages.ERR_INVALID_STORY, ctx.chat_id)

        await self.bot.send_photo(
            ctx.chat_id,
            BufferedInputFile(photo, filename='image.jpg'),
            caption=data.get('story'),
            reply_markup=prepare_buttons({'⏰': ForwardCallback(action=ForwardAction.SCHEDULE)})
        )

    async def async_generate_action(self, ctx: BotContext, action: Callable):
        msg = await self.bot.send_sticker(ctx.chat_id, Stickers.WIP)
        await action(ctx)
        await self.bot.delete_message(ctx.chat_id, msg.message_id)

    async def save_file_to_disk(self, file_id: str) -> str:
        file = await self.bot.get_file(file_id)
        os_path = get_image_path(self.config.BASE_IMAGE_FOLDER, file.file_path)
        await self.bot.download_file(file.file_path, os_path)

        return os_path
