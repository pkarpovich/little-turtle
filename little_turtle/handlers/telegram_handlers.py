from telebot import TeleBot
from telebot.types import Message

from little_turtle.controlles import StoriesController
from little_turtle.services import AppConfig
from little_turtle.utils import story_response


class TelegramHandlers:
    story_controller: StoriesController
    bot: TeleBot

    def __init__(self, config: AppConfig, stories_controller: StoriesController):
        self.story_controller = stories_controller

        self.bot = TeleBot(config.TELEGRAM_BOT_TOKEN)

        @self.bot.message_handler(commands=['start'])
        def start(message: Message):
            self.start_handler(message)

        @self.bot.message_handler(commands=['story'])
        def start(message: Message):
            self.story_handler(message)

    def start_handler(self, message: Message):
        self.bot.reply_to(message, 'Hello, I am Little Turtle!')

    def story_handler(self, message: Message):
        date = message.text.split(' ')[1]

        self.bot.send_chat_action(message.chat.id, 'typing')
        story = self.story_controller.generate_story(date)

        self.bot.reply_to(message, story_response(story))

    def run(self):
        self.bot.infinity_polling()
