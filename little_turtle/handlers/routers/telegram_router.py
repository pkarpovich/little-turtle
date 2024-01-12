import os
from datetime import datetime, timedelta, timezone
from enum import Enum
from os.path import basename
from typing import Union, BinaryIO, Optional
from urllib.parse import urlparse

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, BufferedInputFile, CallbackQuery, URLInputFile

from little_turtle.constants import error_messages, messages
from little_turtle.controlles import StoriesController
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.base_router import BaseRouter
from little_turtle.services import AppConfig, LoggerService, TelegramService
from little_turtle.utils import prepare_buttons, validate_date, get_image_path, read_file_from_disk, pretty_print_json


class ImageCallback(CallbackData, prefix="turtle_image"):
    button: str
    message_id: str


class ForwardAction(str, Enum):
    SUGGEST_STORY = "suggest_story"
    IMAGE_PROMPT = "image_prompt"
    IMAGINE_STORY = "imagine_story"
    SET_DATE = "set_date"
    SET_STORY = "set_story"
    SET_IMAGE_PROMPT = "set_image_prompt"
    SET_IMAGE = "set_image"
    SCHEDULE = "schedule"
    TARGET_TOPIC = "target_topic"
    SELECT_TARGET_TOPIC = "select_target_topic"


class ForwardCallback(CallbackData, prefix="turtle_forward"):
    action: ForwardAction
    payload: Optional[str] = None


class FormState(StatesGroup):
    date = State()
    story = State()
    image_prompt = State()
    image = State()
    target_topics = State()
    comment = State()


class TelegramRouter(BaseRouter):
    def __init__(
            self,
            bot: Bot,
            config_service: AppConfig,
            logger_service: LoggerService,
            telegram_service: TelegramService,
            story_controller: StoriesController,
    ):
        super().__init__(bot)

        self.config = config_service
        self.logger_service = logger_service
        self.story_controller = story_controller
        self.telegram_service = telegram_service

    def get_router(self) -> Router:
        self.router.message(Command("suggest_story"))(self.suggest_story_handler)
        self.router.message(Command("suggest_story_prompt"))(self.suggest_story_prompt_handler)
        self.router.message(Command("imagine_story"))(self.imagine_story_handler)
        self.router.message(Command("set_date"))(self.set_date_handler)
        self.router.message(Command("set_story"))(self.set_story_handler)
        self.router.message(Command("set_image_prompt"))(self.set_image_prompt_handler)
        self.router.message(Command("set_image"))(self.set_image_handler)
        self.router.message(Command("add_target_topic"))(self.add_target_topic_handler)
        self.router.message(Command("set_comment"))(self.set_comment)
        self.router.message(Command("clear_comment"))(self.clear_comment)
        self.router.message(Command("story"))(self.story_handler)
        self.router.message(Command("preview"))(self.preview_handler)
        self.router.message(Command("schedule"))(self.schedule_handler)
        self.router.message(Command("state"))(self.state_handler)
        self.router.message(Command("cancel"))(self.cancel_handler)
        self.router.message(FormState.date)(self.story_date_handler)
        self.router.callback_query(ForwardCallback.filter())(self.forward_click_handler)

        return self.router

    async def story_handler(self, _: Message, ctx: BotContext):
        last_scheduled_story_date = await self.telegram_service.get_last_scheduled_message_date(
            self.config.CHAT_IDS_TO_SEND_STORIES[0]
        )

        if not last_scheduled_story_date:
            return await self.send_message(messages.ASK_DATE, ctx.chat_id)

        raw_next_story_date = last_scheduled_story_date + timedelta(days=1)
        next_story_date = raw_next_story_date.strftime('%d.%m.%Y')
        await ctx.state.set_state(None)

        topics = await self.__suggest_target_topics(next_story_date, ctx)
        await self.__add_target_topic(topics[0], ctx)

        story = await self.__generate_story(next_story_date, ctx)
        await self.__set_story(story, ctx)

        image_prompt = await self.__generate_image_prompt(story, ctx.chat_id)
        await self.__set_image_prompt(image_prompt, ctx)

        await self.__generate_image(image_prompt, ctx.chat_id)

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

    async def state_handler(self, _: Message, ctx: BotContext):
        data = await ctx.state.get_data()
        if not data:
            return await self.send_message(messages.NO_STATE, ctx.chat_id)

        await self.send_message(
            pretty_print_json(data),
            ctx.chat_id
        )

    async def cancel_handler(self, _: Message, ctx: BotContext):
        await ctx.state.clear()
        await self.send_message(messages.RESET_STORY, ctx.chat_id)

    async def story_date_handler(self, message: Message, ctx: BotContext):
        date = message.text

        if not await self.__set_date(date, ctx):
            return

        await ctx.state.set_state(None)
        await self.__generate_story(date, ctx)

    async def suggest_story_handler(self, message: Message, ctx: BotContext):
        if not await self.__validate_story_date(message, ctx.chat_id):
            return

        await self.__generate_story(message.reply_to_message.text, ctx)

    async def suggest_story_prompt_handler(self, message: Message, ctx: BotContext):
        if not await self.__validate_story_msg(message, ctx.chat_id):
            return

        await self.__generate_image_prompt(message.reply_to_message.text, ctx.chat_id)

    async def imagine_story_handler(self, message: Message, ctx: BotContext):
        if not await self.__validate_image_prompt_msg(message, ctx.chat_id):
            return

        await self.__generate_image(message.reply_to_message.text, ctx.chat_id)

    async def set_date_handler(self, message: Message, ctx: BotContext):
        if not await self.__validate_story_date(message, ctx.chat_id):
            return

        await self.send_message(
            messages.SUGGEST_TARGET_TOPICS,
            ctx.chat_id,
        )

        await self.__suggest_target_topics(message.reply_to_message.text, ctx)

        await self.__set_date(message.reply_to_message.text, ctx)

    async def set_story_handler(self, message: Message, ctx: BotContext):
        if not await self.__validate_story_msg(message, ctx.chat_id):
            return

        await self.__set_story(message.reply_to_message.text, ctx)

    async def set_image_prompt_handler(self, message: Message, ctx: BotContext):
        if not await self.__validate_image_prompt_msg(message, ctx.chat_id):
            return

        await self.__set_image_prompt(message.reply_to_message.text, ctx)

    async def set_image_handler(self, message: Message, ctx: BotContext):
        if not await self.__validate_image_msg(message, ctx.chat_id):
            return

        await self.__set_image(message.reply_to_message.photo[-1].file_id, ctx)

    async def add_target_topic_handler(self, message: Message, ctx: BotContext):
        if not await self.__validate_story_topic_msg(message, ctx.chat_id):
            return

        await self.__add_target_topic(message.reply_to_message.text, ctx)

    async def set_comment(self, message: Message, ctx: BotContext):
        if not message.reply_to_message or not message.reply_to_message.text:
            return await self.send_message(error_messages.ERR_NO_REPLY_MSG, ctx.chat_id)

        await ctx.state.update_data(comment=message.reply_to_message.text)
        await self.send_message(messages.SET_COMMENT, ctx.chat_id)

    async def clear_comment(self, _: Message, ctx: BotContext):
        await ctx.state.update_data(comment=None)
        await self.send_message(messages.CLEAR_COMMENT, ctx.chat_id)

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
        await query.answer(messages.ACTION_IN_PROGRESS)
        data = await ctx.state.get_data()

        match callback_data.action:
            case ForwardAction.SUGGEST_STORY:
                await self.__generate_story(data.get('date'), ctx)

            case ForwardAction.IMAGE_PROMPT:
                await self.__generate_image_prompt(data.get('story'), ctx.chat_id)

            case ForwardAction.IMAGINE_STORY:
                await self.__generate_image(data.get('image_prompt'), ctx.chat_id)

            case ForwardAction.SET_DATE:
                await self.__set_date(query.message.text, ctx)

            case ForwardAction.SET_STORY:
                await self.__set_story(query.message.text, ctx)

            case ForwardAction.SET_IMAGE_PROMPT:
                await self.__set_image_prompt(query.message.text, ctx)

            case ForwardAction.SET_IMAGE:
                await self.__set_image(query.message.photo[-1].file_id, ctx)

            case ForwardAction.TARGET_TOPIC:
                await self.__add_target_topic(query.message.text, ctx)

            case ForwardAction.SCHEDULE:
                photo, photo_name = await self.__get_file(query.message.photo[-1].file_id)
                text = data.get('story')
                date = await self.__prepare_schedule_date(data.get('date'))
                await self.__schedule_story(date, text, photo, photo_name, ctx)
                await ctx.state.clear()

            case ForwardAction.SELECT_TARGET_TOPIC:
                topics = self.__split_target_topics(query.message.text)
                await self.__add_target_topic(topics[int(callback_data.payload) - 1], ctx)

    async def send_morning_message(self):
        for chat_id in self.config.USER_IDS_TO_SEND_MORNING_MSG:
            await self.telegram_service.send_message(chat_id, '/story')

    async def __generate_story(self, date: str, ctx: BotContext, skip_status_messages: bool = False) -> Optional[str]:
        if not validate_date(date):
            await self.send_message(error_messages.ERR_INVALID_INPUT_DATE, ctx.chat_id)
            return

        if not skip_status_messages:
            await self.send_message(messages.STORY_GENERATION_IN_PROGRESS, ctx.chat_id)

        data = await ctx.state.get_data()
        target_topics = data.get('target_topics', list())
        generation_comment = data.get('comment', "")

        story = self.story_controller.suggest_story(date, target_topics, generation_comment)
        await self.send_message(
            story,
            chat_id=ctx.chat_id,
            buttons=prepare_buttons(
                {
                    '🔁': ForwardCallback(action=ForwardAction.SUGGEST_STORY),
                    '🌠': ForwardCallback(action=ForwardAction.IMAGE_PROMPT),
                    '🎯': ForwardCallback(action=ForwardAction.SET_STORY),
                }
            )
        )

        return story

    async def __generate_image_prompt(self, text: str, chat_id: int) -> Optional[str]:
        await self.send_message(messages.IMAGE_PROMPT_GENERATION_IN_PROGRESS, chat_id, show_typing=True)

        image_prompt = self.story_controller.suggest_story_prompt(text)
        await self.send_message(
            image_prompt,
            chat_id=chat_id,
            buttons=prepare_buttons(
                {
                    '🔁': ForwardCallback(action=ForwardAction.IMAGE_PROMPT),
                    '🎨': ForwardCallback(action=ForwardAction.IMAGINE_STORY),
                    '🎯': ForwardCallback(action=ForwardAction.SET_IMAGE_PROMPT),
                }
            )
        )

        return image_prompt

    async def __generate_image(self, image_prompt: str, chat_id: int):
        await self.send_message(messages.IMAGE_GENERATION_IN_PROGRESS, chat_id, show_typing=True)

        image_url = self.story_controller.imagine_story(image_prompt)

        image = URLInputFile(image_url, filename=os.path.basename(urlparse(image_url).path))
        return await self.bot.send_photo(
            chat_id,
            image,
            reply_markup=prepare_buttons(
                {
                    '🔁': ForwardCallback(action=ForwardAction.IMAGINE_STORY),
                    '🎯': ForwardCallback(action=ForwardAction.SET_IMAGE),
                }
            )
        )

    async def __set_date(self, date: str, ctx: BotContext) -> bool:
        if not validate_date(date):
            await self.send_message(error_messages.ERR_INVALID_INPUT_DATE, ctx.chat_id)
            return False

        await ctx.state.update_data(date=date)
        await self.send_message(messages.REMEMBER_INPUT_DATE, ctx.chat_id)

        return True

    async def __set_story(self, story: str, ctx: BotContext):
        await ctx.state.update_data(story=story)
        await self.send_message(messages.REMEMBER_INPUT_STORY, ctx.chat_id)

    async def __set_image_prompt(self, image_prompt: str, ctx: BotContext):
        await ctx.state.update_data(image_prompt=image_prompt)
        await self.send_message(messages.REMEMBER_INPUT_IMAGE_PROMPT, ctx.chat_id)

    async def __set_image(self, file_id: str, ctx: BotContext):
        image_path = await self.__save_file_to_disk(file_id)

        await ctx.state.update_data(image=image_path)
        await self.send_message(messages.REMEMBER_INPUT_IMAGE, ctx.chat_id)

    async def __add_target_topic(self, target_topic: str, ctx: BotContext):
        data = await ctx.state.get_data()

        target_topics: [str] = data.get('target_topics') or list()
        target_topics.append(target_topic)

        await ctx.state.update_data(target_topics=target_topics)
        await self.send_message(messages.REMEMBER_TARGET_TOPIC, ctx.chat_id)

    async def __suggest_target_topics(self, date: str, ctx: BotContext) -> [str]:
        topics = self.story_controller.suggest_on_this_day_events(date)
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

        return self.__split_target_topics(topics)

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

    @staticmethod
    def __split_target_topics(target_topics: str) -> [str]:
        return target_topics.split('\n\n')

    async def __validate_story_date(self, message: Message, chat_id: int) -> bool:
        if not message.reply_to_message or not message.reply_to_message.text:
            await self.send_message(error_messages.ERR_NO_REPLY_DATE, chat_id)
            return False

        return True

    async def __validate_story_msg(self, message: Message, chat_id: int) -> bool:
        if not message.reply_to_message or not message.reply_to_message.text:
            await self.send_message(error_messages.ERR_NO_REPLY_STORY, chat_id)
            return False

        return True

    async def __validate_image_prompt_msg(self, message: Message, chat_id: int) -> bool:
        if not message.reply_to_message or not message.reply_to_message.text:
            await self.send_message(error_messages.ERR_NO_REPLY_IMAGE_PROMPT, chat_id)
            return False

        return True

    async def __validate_image_msg(self, message: Message, chat_id: int) -> bool:
        if (
                not message.reply_to_message
                or not message.reply_to_message.photo
                or not len(message.reply_to_message.photo) > 1
        ):
            await self.send_message(error_messages.ERR_NO_REPLY_IMAGE, chat_id)
            return False

        return True

    async def __validate_story_topic_msg(self, message: Message, chat_id: int) -> bool:
        if not message.reply_to_message or not message.reply_to_message.text:
            await self.send_message(error_messages.ERR_NO_REPLY_STORY_TOPIC, chat_id)
            return False

        return True
