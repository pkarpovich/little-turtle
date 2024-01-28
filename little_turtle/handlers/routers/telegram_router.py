from datetime import datetime, timedelta, timezone
from os.path import basename
from typing import Union, BinaryIO

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, BufferedInputFile, CallbackQuery

from little_turtle.constants import error_messages, messages, ReplyKeyboardItems
from little_turtle.controlles import StoriesController
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.actions import ForwardCallback, ForwardAction
from little_turtle.handlers.routers.base.base_stories_router import BaseStoriesRouter
from little_turtle.services import AppConfig, LoggerService, TelegramService
from little_turtle.utils import prepare_buttons, validate_date, get_image_path, read_file_from_disk


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


class TelegramRouter(BaseStoriesRouter):
    def __init__(
            self,
            bot: Bot,
            config_service: AppConfig,
            logger_service: LoggerService,
            telegram_service: TelegramService,
            story_controller: StoriesController,
    ):
        super().__init__(bot, story_controller)

        self.config = config_service
        self.logger_service = logger_service
        self.story_controller = story_controller
        self.telegram_service = telegram_service

    def get_router(self) -> Router:
        self.router.message(Command("story"))(self.story_handler)
        self.router.message(Command("preview"))(self.preview_handler)
        self.router.message(Command("schedule"))(self.schedule_handler)
        self.router.message()(self.handle_message)

        return self.router

    async def handle_message(self, message: Message, ctx: BotContext):
        data = await ctx.state.get_data()

        match message.text:
            case ReplyKeyboardItems.STORY.value:
                await self.set_message_reaction(ctx.chat_id, ctx.message.message_id, '👍')
                await self.__generate_story(data.get('date'), ctx)
            case ReplyKeyboardItems.IMAGE_PROMPT.value:
                await self.__generate_image_prompt(data.get('story'), ctx.chat_id)
            case ReplyKeyboardItems.IMAGE.value:
                await self.__generate_image(data.get('image_prompt'), ctx.chat_id)
            case ReplyKeyboardItems.STATE.value:
                await self.state_handler(message, ctx)
            case ReplyKeyboardItems.PREVIEW.value:
                await self.preview_handler(message, ctx)
            case ReplyKeyboardItems.CANCEL.value:
                await self.cancel_handler(message, ctx)

    async def story_handler(self, _: Message, ctx: BotContext):
        last_scheduled_story_date = await self.telegram_service.get_last_scheduled_message_date(
            self.config.CHAT_IDS_TO_SEND_STORIES[0]
        )

        if not last_scheduled_story_date:
            return await self.send_message(messages.ASK_DATE, ctx.chat_id)

        raw_next_story_date = last_scheduled_story_date + timedelta(days=1)
        next_story_date = raw_next_story_date.strftime('%d.%m.%Y')

        topics = await self.__suggest_target_topics(next_story_date, ctx)
        await self.__add_target_topic(topics[0], ctx)

        story = await self.generate_story(ctx)
        await ctx.state.update_data(story=story)

        image_prompt = await self.generate_image_prompt(ctx)
        await ctx.state.update_data(image_prompt=image_prompt)

        await self.generate_image(ctx)

    async def preview_handler(self, _: Message, ctx: BotContext):
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

    async def schedule_handler(self, message: Message, ctx: BotContext):
        raw_date = message.text.split(' ')[-1]

        if not raw_date or not validate_date(raw_date):
            return await self.send_message(error_messages.ERR_INVALID_INPUT_DATE, message.chat.id)

        if not message.reply_to_message or not message.reply_to_message.caption:
            return await self.send_message(error_messages.ERR_INVALID_STORY, message.chat.id)
        text = message.reply_to_message.caption

        if (
                not message.reply_to_message
                or not message.reply_to_message.photo
                or not len(message.reply_to_message.photo) > 0
        ):
            return await self.send_message(error_messages.ERR_NO_STORY_PHOTO, message.chat.id)
        photo, photo_name = await self.__get_file(message.reply_to_message.photo[-1].file_id)

        date = await self.__prepare_schedule_date(raw_date)
        await self.__schedule_story(date, text, photo, photo_name, ctx)

    async def forward_click_handler(self, query: CallbackQuery, callback_data: ForwardCallback, ctx: BotContext):
        data = await ctx.state.get_data()
        await query.answer("Will be processed soon", )

        match callback_data.action:
            case ForwardAction.SCHEDULE:
                photo, photo_name = await self.__get_file(query.message.photo[-1].file_id)
                text = data.get('story')
                date = await self.__prepare_schedule_date(data.get('date'))
                await self.__schedule_story(date, text, photo, photo_name, ctx)
                await ctx.state.clear()

    async def send_morning_message(self):
        for chat_id in self.config.USER_IDS_TO_SEND_MORNING_MSG:
            await self.telegram_service.send_message(chat_id, '/story')

    async def __schedule_story(self, date: datetime, text: str, photo: BinaryIO, photo_name: str, ctx: BotContext):
        for chat_id in self.config.CHAT_IDS_TO_SEND_STORIES:
            self.logger_service.info(
                "Sending scheduled story",
                chat_id=chat_id,
                date=date,
            )
            await self.telegram_service.send_photo(
                chat_id,
                photo,
                photo_name,
                text,
                date,
            )
            photo.seek(0)

        await self.send_message(messages.SEND_SCHEDULE_STORY, ctx.chat_id)

    async def __get_file(self, file_id: str) -> [BinaryIO, str]:
        file = await self.bot.get_file(file_id)
        return await self.bot.download_file(file.file_path), basename(file.file_path)

    async def __save_file_to_disk(self, file_id: str) -> str:
        file = await self.bot.get_file(file_id)
        os_path = get_image_path(self.config.BASE_IMAGE_FOLDER, file.file_path)
        await self.bot.download_file(file.file_path, os_path)

        return os_path

    async def __prepare_schedule_date(self, date: str) -> Union[datetime, None]:
        try:
            tz = timezone(timedelta(hours=self.config.DEFAULT_TZ))

            date_obj = datetime.strptime(date, '%d.%m.%Y')
            return date_obj.replace(
                hour=self.config.DEFAULT_SCHEDULE_HOUR,
                minute=self.config.DEFAULT_SCHEDULE_MINUTE,
                second=self.config.DEFAULT_SCHEDULE_SECOND,
                tzinfo=tz
            )
        except (ValueError, IndexError):
            return None
