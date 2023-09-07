import asyncio
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Optional, BinaryIO, Union

import pytz
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, URLInputFile, CallbackQuery, InlineKeyboardMarkup, ErrorEvent
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from little_turtle.controlles import StoriesController
from little_turtle.services import AppConfig, LoggerService, TelegramService, ErrorHandlerService
from little_turtle.stores import Story, HistoryStore, HistoryItem
from little_turtle.utils import story_response, prepare_buttons


class ImageCallback(CallbackData, prefix="turtle_image"):
    button: str
    message_id: str


class ForwardAction(str, Enum):
    SUGGEST_STORY = "suggest_story"
    IMAGE_PROMPT = "image_prompt"
    IMAGINE_STORY = "imagine_story"


class OriginalMessageType(str, Enum):
    STORY = "story"
    IMAGE_PROMPT = "image_prompt"
    IMAGE = "image"


class ForwardCallback(CallbackData, prefix="turtle_forward"):
    original_message_type: OriginalMessageType
    action: ForwardAction
    data: Optional[str]


class TelegramHandlers:
    history_store: HistoryStore
    story_controller: StoriesController
    logger_service: LoggerService
    bot: Bot

    def __init__(
            self,
            config: AppConfig,
            stories_controller: StoriesController,
            history_store: HistoryStore,
            logger_service: LoggerService,
            telegram_service: TelegramService,
            error_handler_service: ErrorHandlerService,
    ):
        self.error_handler_service = error_handler_service
        self.story_controller = stories_controller
        self.telegram_service = telegram_service
        self.logger_service = logger_service
        self.history_store = history_store
        self.config = config

        self.bot = Bot(config.TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()
        self.scheduler = AsyncIOScheduler()

        self.__on_startup(self.dp)

    def __on_startup(self, dispatcher: Dispatcher):
        self.logger_service.info("Starting up turtle... 🐢")

        @dispatcher.message(lambda message: message.from_user.id not in self.config.TELEGRAM_ALLOWED_USERS)
        async def handle_disallowed_users(message: Message):
            self.logger_service.info(
                "Disallowed user tried to use the bot",
                user_id=message.from_user.id,
                user_message=message
            )
            await self.__send_message(
                "Sorry, I don't know you! 🐢🤔",
                message.chat.id,
                skip_message_history=True,
            )

        @dispatcher.message(CommandStart())
        async def start(message: Message):
            await self.start_handler(message)

        @dispatcher.message(Command("ping"))
        async def ping(message: Message):
            await self.__send_message(
                "Pong! 🐢🏓",
                message.chat.id,
                message.message_id,
                skip_message_history=True,
            )

        @dispatcher.message(Command("story"))
        async def start(message: Message):
            await self.story_handler(message)

        @dispatcher.message(Command("suggest_story_prompt"))
        async def suggest_story_prompt(message: Message):
            await self.suggest_story_prompt_handler(message)

        @dispatcher.message(Command("imagine_story"))
        async def imagine_story(message: Message):
            await self.imagine_story_handler(message)

        @dispatcher.message(Command("suggest_story"))
        async def suggest_story(message: Message):
            await self.suggest_story_handler(message)

        @dispatcher.message(Command("schedule"))
        async def schedule(message: Message):
            await self.schedule_handler(message)

        @dispatcher.callback_query(ImageCallback.filter())
        async def button_click(query: CallbackQuery, callback_data: ImageCallback):
            await self.button_click_handler(query, callback_data)

        @dispatcher.callback_query(ForwardCallback.filter())
        async def forward_click(query: CallbackQuery, callback_data: ForwardCallback):
            await self.forward_click_handler(query, callback_data)

        @dispatcher.error()
        async def error_handler(event: ErrorEvent):
            self.logger_service.info("Error while handling update", exc_info=event.exception)
            self.error_handler_service.capture_exception(event.exception)

            if event.update.callback_query is not None:
                chat_id = event.update.callback_query.message.chat.id
            elif event.update.message is not None:
                chat_id = event.update.message.chat.id
            else:
                return

            await self.__send_message(
                "Sorry, I'm having trouble processing your request! 🐢🤔",
                chat_id,
                skip_message_history=True,
            )

    @staticmethod
    async def start_handler(message: Message):
        await message.answer("Hello, I am Little Turtle!")

    async def story_handler(self, message: Message):
        date = message.reply_to_message.text or message.text.split(' ')[1]
        story = self.story_controller.generate_story(date)

        await self.__send_message(
            story_response(story),
            message.chat.id,
            message.message_id,
            show_typing=True,
        )

    async def imagine_story_handler(self, message: Message):
        image_prompt = message.reply_to_message.text

        await self.__generate_image(image_prompt, message.chat.id)

    async def suggest_story_prompt_handler(self, message: Message):
        text = message.reply_to_message.text

        await self.__generate_image_prompt(text, message.chat.id, message.message_id)

    async def suggest_story_handler(self, message: Message):
        date = message.reply_to_message.text or message.text.split(' ')[1]

        await self.__generate_story(date, message.chat.id, message.message_id)

    async def schedule_handler(self, message: Message):
        photo = await self.__get_file(message.reply_to_message.photo[-1].file_id)
        text = message.reply_to_message.caption

        date = await self.__prepare_schedule_date(message.text)
        if not date:
            await self.__send_message(
                "Sorry, I don't understand this date! 🐢🤔",
                message.chat.id,
                message.message_id,
                skip_message_history=True,
            )
            return

        for chat_id in self.config.CHAT_IDS_TO_SEND_STORIES:
            self.logger_service.info(
                "Sending scheduled story",
                chat_id_type=type(chat_id),
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

        await self.__send_message(
            "Alright, I'll send this story to the channels! 🐢📲",
            message.chat.id,
            message.message_id,
            skip_message_history=True,
        )

    async def button_click_handler(self, query: CallbackQuery, callback_data: ImageCallback):
        await query.answer(f"You clicked {callback_data.button} button!")

        message = self.story_controller.trigger_button(callback_data.button, callback_data.message_id)
        await self.__wait_for_message(message['messageId'], query.message.chat.id)

    async def forward_click_handler(self, query: CallbackQuery, callback_data: ForwardCallback):
        await query.answer("Working on it! 🐢")
        chat_id = query.message.chat.id
        message_id = query.message.message_id
        original_message_type = callback_data.original_message_type

        match callback_data.action:
            case ForwardAction.SUGGEST_STORY:
                await self.__generate_story(callback_data.data, chat_id, message_id)

            case ForwardAction.IMAGE_PROMPT:
                reply_id = query.message.reply_to_message.message_id
                target_message_id = reply_id \
                    if original_message_type == OriginalMessageType.IMAGE_PROMPT \
                    else message_id

                original_message_id = callback_data.data \
                    if callback_data.data != "" and original_message_type == OriginalMessageType.IMAGE_PROMPT \
                    else message_id

                message = self.history_store.get_by_message_id(target_message_id)
                await self.__generate_image_prompt(message['content'], chat_id, original_message_id)

            case ForwardAction.IMAGINE_STORY:
                message = self.history_store.get_by_message_id(message_id)
                await self.__generate_image(message['content'], chat_id)

    async def send_morning_message(self):
        next_week_date = datetime.now() + timedelta(days=7)
        formatted_date = next_week_date.strftime('%d.%m.%Y')

        await self.__generate_story(formatted_date, self.config.TELEGRAM_ADMIN_ID, None, True)

    async def __generate_story(
            self,
            date: str,
            chat_id: int,
            reply_id: Optional[int],
            skip_status_messages: bool = False
    ):
        if not skip_status_messages:
            await self.__send_message(
                'Crafting a fresh tale just for you! 🐢📜 Hang tight!',
                chat_id,
                skip_message_history=True,
            )

        story = self.story_controller.suggest_story(date)
        await self.__send_message(
            story['content'],
            chat_id=chat_id,
            reply_id=reply_id,
            buttons=prepare_buttons(
                {
                    '🔁': ForwardCallback(
                        original_message_type=OriginalMessageType.STORY,
                        action=ForwardAction.SUGGEST_STORY,
                        data=date
                    ),
                    '🌠': ForwardCallback(
                        original_message_type=OriginalMessageType.STORY,
                        action=ForwardAction.IMAGE_PROMPT,
                        data=date
                    ),
                }
            )
        )

    async def __generate_image_prompt(self, text: str, chat_id: int, reply_id: int):
        await self.__send_message(
            'Getting ready to craft a new visual masterpiece! 🐢🎨 Hold on to your shell!',
            chat_id,
            skip_message_history=True,
            show_typing=True,
        )

        story = self.story_controller.suggest_story_prompt(Story(content=text, image_prompt=''))
        await self.__send_message(
            story['image_prompt'],
            chat_id=chat_id,
            reply_id=reply_id,
            buttons=prepare_buttons(
                {
                    '🔁': ForwardCallback(
                        action=ForwardAction.IMAGE_PROMPT,
                        original_message_type=OriginalMessageType.IMAGE_PROMPT,
                        data=str(reply_id)
                    ),
                    '🎨': ForwardCallback(
                        action=ForwardAction.IMAGINE_STORY,
                        original_message_type=OriginalMessageType.IMAGE_PROMPT,
                        data=""
                    ),
                }
            )
        )

    async def __generate_image(self, image_prompt: str, chat_id: int):
        await self.__send_message(
            'Alright, diving deep into my turtle thoughts to conjure your tale... 🐢🤔✍️',
            chat_id,
            skip_message_history=True,
            show_typing=True,
        )

        image = self.story_controller.imagine_story(image_prompt)
        await self.__wait_for_message(image['messageId'], chat_id)

    async def __wait_for_message(self, message_id: str, chat_id: int):
        last_message_id = None
        attempts = 0

        while True:
            if attempts > self.config.MAX_IMAGE_GEN_ATTEMPTS:
                await self.__send_message(
                    "Sorry, I'm having trouble generating your image! 🐢🤔",
                    chat_id,
                    skip_message_history=True,
                )
                return

            image_status = self.story_controller.get_image_status(message_id)

            if last_message_id:
                await self.bot.delete_message(chat_id, last_message_id)

            status_message = await self.__send_message(
                f"Starting to paint our virtual canvas: {image_status['progress']}% complete! 🐢🎨",
                chat_id,
                skip_message_history=True,
            )
            last_message_id = status_message.message_id

            if image_status['progress'] != 100:
                attempts += 1
                await asyncio.sleep(self.config.IMAGE_GEN_ATTEMPTS_DELAY)
                continue

            image_url = image_status['response']['imageUrl']
            buttons = image_status['response']['buttons']

            reply_markup = prepare_buttons(
                dict(
                    map(
                        lambda button: (
                            button,
                            ImageCallback(
                                message_id=image_status['response']['buttonMessageId'],
                                button=button,
                            )
                        ),
                        buttons
                    )
                ),
            )

            image = URLInputFile(image_url)
            await self.bot.delete_message(chat_id, last_message_id)
            return await self.bot.send_photo(chat_id, image, reply_markup=reply_markup)

    async def __send_message(
            self,
            message: str,
            chat_id: int,
            reply_id: int = None,
            silent: bool = True,
            show_typing: bool = False,
            skip_message_history: bool = False,
            buttons: InlineKeyboardMarkup = None
    ) -> Message:
        if show_typing:
            await self.bot.send_chat_action(chat_id, 'typing')

        message = await self.bot.send_message(
            chat_id,
            message,
            reply_to_message_id=reply_id,
            disable_notification=silent,
            reply_markup=buttons
        )

        if not skip_message_history:
            self.history_store.create(HistoryItem(
                message_id=message.message_id,
                user_id=message.from_user.id,
                chat_id=message.chat.id,
                created_at=message.date,
                content=message.text,
            ))

        return message

    async def __get_file(self, file_id: str) -> BinaryIO:
        file = await self.bot.get_file(file_id)
        return await self.bot.download_file(file.file_path)

    async def __prepare_schedule_date(self, text: str) -> Union[datetime, None]:
        try:
            tz = timezone(timedelta(hours=self.config.DEFAULT_TZ))

            raw_date = text.split(maxsplit=1)[1]

            if not raw_date:
                return None

            date_obj = datetime.strptime(raw_date, '%d.%m.%Y')
            return date_obj.replace(
                hour=self.config.DEFAULT_SCHEDULE_HOUR,
                minute=self.config.DEFAULT_SCHEDULE_MINUTE,
                second=self.config.DEFAULT_SCHEDULE_SECOND,
                tzinfo=tz
            )
        except (ValueError, IndexError):
            return None

    async def run(self):
        self.scheduler.add_job(
            self.send_morning_message,
            CronTrigger(hour=8, minute=0, timezone=pytz.timezone('Europe/Warsaw'))
        )
        self.scheduler.start()

        self.logger_service.info("Telegram turtle is all set and eager to assist! 🐢📲 Just send a command!")
        await self.dp.start_polling(self.bot)
