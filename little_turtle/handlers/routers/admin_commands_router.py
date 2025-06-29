from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message

from little_turtle.controlles import StoriesController
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.base.base_stories_router import BaseStoriesRouter
from little_turtle.services import AppConfig, TelegramService


class ImageCallback(CallbackData, prefix="turtle_image"):
    button: str
    message_id: str


class FormState(StatesGroup):
    date = State()
    story = State()
    image_prompt = State()
    image = State()
    target_topics = State()
    comment = State()


class AdminCommandsRouter(BaseStoriesRouter):
    def __init__(
        self,
        bot: Bot,
        config_service: AppConfig,
        telegram_service: TelegramService,
        story_controller: StoriesController,
    ):
        super().__init__(bot, story_controller, config_service)

        self.config = config_service
        self.telegram_service = telegram_service

    def get_router(self) -> Router:
        self.router.message(Command("story"))(self.story_handler)
        self.router.message(Command("preview"))(self.preview_handler)

        return self.router

    async def send_morning_message(self):
        for chat_id in self.config.USER_IDS_TO_SEND_MORNING_MSG:
            await self.telegram_service.send_message(chat_id, "/story")

    async def story_handler(self, _: Message, ctx: BotContext):
        next_story_date = await self.story_controller.get_next_story_date()
        await ctx.state.update_data(date=next_story_date)
        await self.send_message(next_story_date, ctx.chat_id)

        topics = await self.suggest_target_topics(ctx)
        await self.set_target_topic(topics.events[0], ctx)

        story = await self.generate_story(ctx)
        await ctx.state.update_data(story=story)

        image_prompt = await self.generate_image_prompt(ctx)
        await ctx.state.update_data(image_prompt=image_prompt)

        await self.generate_image(ctx)

    async def preview_handler(self, _: Message, ctx: BotContext):
        await self.preview_story(ctx)
