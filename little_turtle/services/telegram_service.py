from datetime import datetime
from typing import Union

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

    async def send_message(self, chat_id: Union[str, int], message: str, schedule: datetime):
        await self.client.send_message(
            chat_id,
            message,
            schedule=schedule,
        )

    async def send_photo(self, chat_id: Union[str, int], photo: str, message: str, schedule: datetime):
        await self.client.send_file(
            chat_id,
            photo,
            caption=message,
            schedule=schedule,
        )

    async def get_chats(self, limit: int) -> list[dict]:
        chats = []

        async for chat in self.client.iter_dialogs(limit=limit):
            chats.append({
                "id": chat.id,
                "name": chat.name,
            })

        return chats
