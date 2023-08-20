from telethon import TelegramClient

from little_turtle.services import AppConfig


class TelegramService:
    client: TelegramClient = None

    def __init__(self, config: AppConfig):
        self.client = TelegramClient(
            config.TELEGRAM_SESSION_NAME,
            config.TELEGRAM_API_ID,
            config.TELEGRAM_API_HASH
        )

    async def login(self):
        await self.client.start()

    async def get_messages(self, chat_id: str = None) -> list[str]:
        messages = []

        async for msg in self.client.iter_messages(chat_id):
            if msg.message is None:
                continue

            messages.append(msg.message)

        return messages
