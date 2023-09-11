import asyncio
import os
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import BinaryIO, Union
from urllib.parse import urlparse

from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, BufferedInputFile, CallbackQuery, URLInputFile

from little_turtle.controlles import StoriesController
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.base_router import BaseRouter
from little_turtle.services import AppConfig, LoggerService, TelegramService
from little_turtle.stores import Story
from little_turtle.utils import prepare_buttons, validate_date, get_image_path, read_file_from_disk


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


class ForwardCallback(CallbackData, prefix="turtle_forward"):
    action: ForwardAction


class FormState(StatesGroup):
    date = State()
    story = State()
    image_prompt = State()
    image = State()


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
        self.router.message(Command("suggest_story_prompt"))(self.suggest_story_prompt_handler)
        self.router.message(Command("suggest_story"))(self.suggest_story_handler)
        self.router.message(Command("imagine_story"))(self.imagine_story_handler)
        self.router.message(Command("set_image_prompt"))(self.set_image_prompt_handler)
        self.router.message(Command("set_image"))(self.set_image_handler)
        self.router.message(Command("set_story"))(self.set_story_handler)
        self.router.message(Command("set_date"))(self.set_date_handler)
        self.router.message(Command("story"))(self.story_handler)
        self.router.message(Command("preview"))(self.preview_handler)
        self.router.message(Command("schedule"))(self.schedule_handler)
        self.router.message(Command("cancel"))(self.cancel_handler)
        self.router.message(FormState.date)(self.story_date_handler)
        self.router.callback_query(ForwardCallback.filter())(self.forward_click_handler)
        self.router.callback_query(ImageCallback.filter())(self.image_button_click_handler)

        return self.router

    async def story_handler(self, _: Message, ctx: BotContext):
        await ctx.state.clear()
        await ctx.state.set_state(FormState.date)
        await self.send_message(
            "Alright, what date do you want the story for? 🐢📜 (dd.mm.yyyy)",
            ctx.chat_id
        )

    async def preview_handler(self, _: Message, ctx: BotContext):
        data = await ctx.state.get_data()
        if not data:
            return await self.send_message(
                "Sorry, I don't have anything to preview! 🐢🤔",
                ctx.chat_id
            )

        date = data.get('date')
        if not date or not validate_date(date):
            return await self.send_message(
                "Sorry, I don't understand this date! 🐢🤔",
                ctx.chat_id
            )

        photo_path = data.get('image')
        if not photo_path:
            return await self.send_message(
                "Sorry, I don't have photo for this story! 🐢🤔",
                ctx.chat_id
            )

        photo = read_file_from_disk(photo_path)
        if not photo:
            return await self.send_message(
                "Sorry, I can't recognize story photo! 🐢🤔",
                ctx.chat_id
            )

        story = data.get('story')
        if not story:
            return await self.send_message(
                "Sorry, I don't have story! 🐢🤔",
                ctx.chat_id,
            )

        await self.bot.send_photo(
            ctx.chat_id,
            BufferedInputFile(photo, filename='image.jpg'),
            caption=data.get('story'),
            reply_markup=prepare_buttons({'⏰': ForwardCallback(action=ForwardAction.SCHEDULE)})
        )

    async def cancel_handler(self, _: Message, ctx: BotContext):
        await ctx.state.clear()
        await self.send_message(
            "Alright, I'll forget everything! 🐢🤔",
            ctx.chat_id
        )

    async def story_date_handler(self, message: Message, ctx: BotContext):
        date = message.text

        if not await self.__set_date(date, ctx):
            return

        await ctx.state.set_state(None)
        await self.__generate_story(date, ctx.chat_id)

    async def suggest_story_handler(self, message: Message, ctx: BotContext):
        await self.__generate_story(message.reply_to_message.text, ctx.chat_id)

    async def suggest_story_prompt_handler(self, message: Message, ctx: BotContext):
        await self.__generate_image_prompt(message.reply_to_message.text, ctx.chat_id)

    async def imagine_story_handler(self, message: Message, ctx: BotContext):
        await self.__generate_image(message.reply_to_message.text, ctx.chat_id)

    async def set_date_handler(self, message: Message, ctx: BotContext):
        await self.__set_date(message.reply_to_message.text, ctx)

    async def set_story_handler(self, message: Message, ctx: BotContext):
        await self.__set_story(message.reply_to_message.text, ctx)

    async def set_image_prompt_handler(self, message: Message, ctx: BotContext):
        await self.__set_image_prompt(message.reply_to_message.text, ctx)

    async def set_image_handler(self, message: Message, ctx: BotContext):
        await self.__set_image(message.reply_to_message.photo[-1].file_id, ctx)

    async def schedule_handler(self, message: Message, ctx: BotContext):
        photo = await self.__get_file(message.reply_to_message.photo[-1].file_id)
        text = message.reply_to_message.caption
        raw_date = message.text.split(' ')[-1]

        if not raw_date or not validate_date(raw_date):
            await self.send_message(
                "Sorry, I don't understand this date! 🐢🤔",
                message.chat.id,
                message.message_id
            )
            return

        date = await self.__prepare_schedule_date(raw_date)
        await self.__schedule_story(date, text, photo, ctx)

    async def image_button_click_handler(self, query: CallbackQuery, callback_data: ImageCallback, ctx: BotContext):
        await query.answer("Working on it! 🐢")

        message = self.story_controller.trigger_button(callback_data.button, callback_data.message_id)
        await self.__wait_for_message(message['messageId'], ctx.chat_id)

    async def forward_click_handler(self, query: CallbackQuery, callback_data: ForwardCallback, ctx: BotContext):
        await query.answer("Working on it! 🐢")
        data = await ctx.state.get_data()

        match callback_data.action:
            case ForwardAction.SUGGEST_STORY:
                await self.__generate_story(data.get('date'), ctx.chat_id)

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

            case ForwardAction.SCHEDULE:
                photo = await self.__get_file(query.message.photo[-1].file_id)
                text = data.get('story')
                date = await self.__prepare_schedule_date(data.get('date'))
                await self.__schedule_story(date, text, photo, ctx)
                await ctx.state.clear()

    async def send_morning_message(self):
        next_week_date = datetime.now() + timedelta(days=7)
        formatted_date = next_week_date.strftime('%d.%m.%Y')

        for chat_id in self.config.USER_IDS_TO_SEND_MORNING_MSG:
            await self.send_message(
                formatted_date,
                chat_id,
                buttons=prepare_buttons({'🎯': ForwardCallback(action=ForwardAction.SET_DATE)})
            )
            await self.__generate_story(formatted_date, chat_id, True)

    async def __generate_story(self, date: str, chat_id: int, skip_status_messages: bool = False):
        if not skip_status_messages:
            await self.send_message(
                'Crafting a fresh tale just for you! 🐢📜 Hang tight!',
                chat_id
            )

        story = self.story_controller.suggest_story(date)
        await self.send_message(
            story['content'],
            chat_id=chat_id,
            buttons=prepare_buttons(
                {
                    '🔁': ForwardCallback(action=ForwardAction.SUGGEST_STORY),
                    '🌠': ForwardCallback(action=ForwardAction.IMAGE_PROMPT),
                    '🎯': ForwardCallback(action=ForwardAction.SET_STORY),
                }
            )
        )

    async def __generate_image_prompt(self, text: str, chat_id: int):
        await self.send_message(
            'Getting ready to craft a new visual masterpiece! 🐢🎨 Hold on to your shell!',
            chat_id,
            show_typing=True,
        )

        story = self.story_controller.suggest_story_prompt(Story(content=text, image_prompt=''))
        await self.send_message(
            story['image_prompt'],
            chat_id=chat_id,
            buttons=prepare_buttons(
                {
                    '🔁': ForwardCallback(action=ForwardAction.IMAGE_PROMPT),
                    '🎨': ForwardCallback(action=ForwardAction.IMAGINE_STORY),
                    '🎯': ForwardCallback(action=ForwardAction.SET_IMAGE_PROMPT),
                }
            )
        )

    async def __generate_image(self, image_prompt: str, chat_id: int):
        await self.send_message(
            'Alright, diving deep into my turtle thoughts to conjure your tale... 🐢🤔✍️',
            chat_id,
            show_typing=True,
        )

        image = self.story_controller.imagine_story(image_prompt)
        await self.__wait_for_message(image['messageId'], chat_id)

    async def __wait_for_message(self, message_id: str, chat_id: int):
        last_message_id = None
        attempts = 0

        while True:
            if attempts > self.config.MAX_IMAGE_GEN_ATTEMPTS:
                await self.send_message(
                    "Sorry, I'm having trouble generating your image! 🐢🤔",
                    chat_id,
                )
                return

            image_status = self.story_controller.get_image_status(message_id)

            if last_message_id:
                await self.bot.delete_message(chat_id, last_message_id)

            status_message = await self.send_message(
                f"Starting to paint our virtual canvas: {image_status['progress']}% complete! 🐢🎨",
                chat_id,
            )
            last_message_id = status_message.message_id

            if image_status['progress'] != 100:
                attempts += 1
                await asyncio.sleep(self.config.IMAGE_GEN_ATTEMPTS_DELAY)
                continue

            message_id = image_status['response']['buttonMessageId']
            image_url = image_status['response']['imageUrl']
            buttons = image_status['response']['buttons']
            description = image_status['response']['description']
            image_name = os.path.basename(urlparse(image_url).path)

            await self.bot.delete_message(chat_id, last_message_id)
            if len(image_url) == 0 and len(description) > 0:
                await self.send_message(
                    f"Sorry, I'm having trouble generating your image! 🐢🤔\n\n{description}",
                    chat_id,
                )
                return

            buttons = list(
                map(
                    lambda button: (
                        button,
                        ImageCallback(message_id=message_id, button=button)
                    ),
                    buttons
                )
            )
            buttons.append(('🎯', ForwardCallback(action=ForwardAction.SET_IMAGE)))
            reply_markup = prepare_buttons(dict(buttons))

            image = URLInputFile(image_url, filename=image_name)
            return await self.bot.send_photo(chat_id, image, reply_markup=reply_markup)

    async def __set_date(self, date: str, ctx: BotContext) -> bool:
        if not validate_date(date):
            await self.send_message(
                "Sorry, I don't understand this date! 🐢🤔",
                ctx.chat_id,
            )
            return False

        await ctx.state.update_data(date=date)
        await self.send_message(
            "Alright, I'll remember this date! 🐢📆",
            ctx.chat_id,
        )

        return True

    async def __set_story(self, story: str, ctx: BotContext):
        await ctx.state.update_data(story=story)
        await self.send_message(
            "Alright, I'll remember this story! 🐢📜",
            ctx.chat_id,
        )

    async def __set_image_prompt(self, image_prompt: str, ctx: BotContext):
        await ctx.state.update_data(image_prompt=image_prompt)
        await self.send_message(
            "Alright, I'll remember this image prompt! 🐢🎨",
            ctx.chat_id,
        )

    async def __set_image(self, file_id: str, ctx: BotContext):
        image_path = await self.__save_file_to_disk(file_id)

        await ctx.state.update_data(image=image_path)
        await self.send_message(
            "Alright, I'll remember this image! 🐢🖼️",
            ctx.chat_id,
        )

    async def __schedule_story(self, date: datetime, text: str, photo: BinaryIO, ctx: BotContext):
        for chat_id in self.config.CHAT_IDS_TO_SEND_STORIES:
            self.logger_service.info(
                "Sending scheduled story",
                chat_id=chat_id,
                date=date,
            )
            await self.telegram_service.send_photo(
                chat_id,
                photo,
                text,
                date,
            )
            photo.seek(0)

        await self.send_message(
            "Alright, I'll send this story to the channels! 🐢📲",
            ctx.chat_id
        )

    async def __get_file(self, file_id: str) -> BinaryIO:
        file = await self.bot.get_file(file_id)
        return await self.bot.download_file(file.file_path)

    async def __save_file_to_disk(self, file_id: str) -> str:
        file = await self.bot.get_file(file_id)
        os_path = get_image_path(file.file_path)
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