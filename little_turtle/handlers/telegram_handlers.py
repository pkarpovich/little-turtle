import asyncio

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.filters.callback_data import CallbackData
from aiogram.types import Message, URLInputFile, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from little_turtle.controlles import StoriesController
from little_turtle.services import AppConfig
from little_turtle.stores import Story
from little_turtle.utils import story_response


class ImageCallback(CallbackData, prefix="turtle"):
    action: str
    button: str
    message_id: str


class TelegramHandlers:
    story_controller: StoriesController
    bot: Bot

    def __init__(self, config: AppConfig, stories_controller: StoriesController):
        self.story_controller = stories_controller

        self.bot = Bot(config.TELEGRAM_BOT_TOKEN)
        self.dp = Dispatcher()

        @self.dp.message(CommandStart())
        async def start(message: Message):
            await self.start_handler(message)

        @self.dp.message(Command("story"))
        async def start(message: Message):
            await self.story_handler(message)

        @self.dp.message(Command("suggest_story_prompt"))
        async def suggest_story_prompt(message: Message):
            await self.suggest_story_prompt_handler(message)

        @self.dp.message(Command("imagine_story"))
        async def imagine_story(message: Message):
            await self.imagine_story_handler(message)

        @self.dp.message(Command("suggest_story"))
        async def suggest_story(message: Message):
            await self.suggest_story_handler(message)

        @self.dp.callback_query(ImageCallback.filter())
        async def button_click(query: CallbackQuery, callback_data: ImageCallback):
            await self.button_click_handler(query, callback_data)

    @staticmethod
    async def start_handler(message: Message):
        await message.answer("Hello, I am Little Turtle!")

    async def story_handler(self, message: Message):
        date = message.reply_to_message.text or message.text.split(' ')[1]

        await self.bot.send_chat_action(message.chat.id, 'typing')
        story = self.story_controller.generate_story(date)

        await message.answer(story_response(story))

    async def imagine_story_handler(self, message: Message):
        image_prompt = message.reply_to_message.text

        await self.bot.send_message(
            message.chat.id,
            'Alright, diving deep into my turtle thoughts to conjure your tale... 🐢🤔✍️'
        )

        await self.bot.send_chat_action(message.chat.id, 'typing')
        image = self.story_controller.imagine_story(image_prompt)

        await self.bot.send_message(
            message.chat.id,
            'Holding my turtle breath in anticipation of the image... 🐢🖼️🕰️'
        )
        await self.__wait_for_message(image['messageId'], message.chat.id)

    async def suggest_story_prompt_handler(self, message: Message):
        text = message.reply_to_message.text

        await self.bot.send_message(
            message.chat.id,
            'Getting ready to craft a new visual masterpiece! 🐢🎨 Hold on to your shell!'
        )
        await self.bot.send_chat_action(message.chat.id, 'typing')

        story = self.story_controller.suggest_story_prompt(Story(content=text, image_prompt=''))
        await message.answer(story['image_prompt'])

    async def suggest_story_handler(self, message: Message):
        date = message.reply_to_message.text or message.text.split(' ')[1]

        await self.bot.send_message(
            message.chat.id,
            'Crafting a fresh tale just for you! 🐢📜 Hang tight!'
        )

        story = self.story_controller.suggest_story(date)
        await message.answer(story['content'])

    async def button_click_handler(self, query: CallbackQuery, callback_data: ImageCallback):
        print(callback_data.button, callback_data.message_id)
        message = self.story_controller.trigger_button(callback_data.button, callback_data.message_id)
        await query.answer(f"You clicked {callback_data.button} button!")
        print(message)
        await self.__wait_for_message(message['messageId'], query.message.chat.id)

    async def __wait_for_message(self, message_id: str, chat_id: int):
        last_message_id = None

        while True:
            image_status = self.story_controller.get_image_status(message_id)

            if last_message_id:
                await self.bot.delete_message(chat_id, last_message_id)

            status_message = await self.bot.send_message(
                chat_id,
                f"Starting to paint our virtual canvas: {image_status['progress']}% complete! 🐢🎨"
            )
            last_message_id = status_message.message_id

            if image_status['progress'] == 100:
                image_url = image_status['response']['imageUrl']
                buttons = image_status['response']['buttons']

                print(image_status)

                builder = InlineKeyboardBuilder()

                for button in buttons:
                    builder.add(InlineKeyboardButton(
                        text=button,
                        callback_data=ImageCallback(
                            action="button_click",
                            button=button,
                            message_id=image_status['response']['buttonMessageId']
                        ).pack()
                    ))

                row_lengths = self.__split_buttons(buttons)
                builder.adjust(*row_lengths)

                image = URLInputFile(image_url)
                await self.bot.delete_message(chat_id, last_message_id)
                await self.bot.send_photo(chat_id, image, reply_markup=builder.as_markup())

                break

            await asyncio.sleep(5)

    @staticmethod
    def __split_buttons(buttons: list[str]):
        rows = []
        temp_row = []

        for i, button in enumerate(buttons):
            current_len = len(button)

            # Get the length of the previous and next button, if they exist
            prev_button_len = len(buttons[i - 1]) if i - 1 >= 0 else None
            next_button_len = len(buttons[i + 1]) if i + 1 < len(buttons) else None

            move_to_next = False
            if prev_button_len and next_button_len:
                move_to_next = abs(prev_button_len - current_len) == 1 and abs(current_len - next_button_len) == 1

            if current_len <= 2 and not move_to_next:
                if len(temp_row) + 1 > 4:
                    rows.append(len(temp_row))
                    temp_row = [button]
                else:
                    temp_row.append(button)
            else:
                if temp_row:
                    rows.append(len(temp_row))
                    temp_row = []
                temp_row.append(button)
                rows.append(len(temp_row))
                temp_row = []

        if temp_row:
            rows.append(len(temp_row))

        return rows

    async def run(self):
        print("Telegram turtle is all set and eager to assist! 🐢📲 Just send a command!")
        await self.dp.start_polling(self.bot)
