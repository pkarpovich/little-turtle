import os
from datetime import datetime
from tempfile import NamedTemporaryFile
from typing import Union, BinaryIO, Optional

from telethon import TelegramClient

from little_turtle.app_config import AppConfig


class TelegramService:
    client: TelegramClient = None

    def __init__(self, config: AppConfig):
        session_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), config.TELEGRAM_SESSION_NAME
        )

        self.client = TelegramClient(
            session_path,
            config.TELEGRAM_API_ID,
            config.TELEGRAM_API_HASH,
        )

    async def login(self):
        await self.client.start()
        await self.client.connect()

    async def get_messages(self, chat_id: str = None) -> list[str]:
        await self.ensure_connected()
        messages = []

        async for msg in self.client.iter_messages(chat_id):
            if msg.message is None:
                continue

            messages.append(msg.message)

        return messages

    async def ensure_connected(self):
        if not self.client.is_connected():
            await self.client.start()

    async def send_message(
        self, chat_id: Union[str, int], message: str, schedule: datetime = None
    ):
        await self.ensure_connected()
        await self.client.send_message(
            chat_id,
            message,
            schedule=schedule,
        )

    async def send_photo(
        self,
        chat_id: Union[str, int],
        photo: BinaryIO,
        photo_name: str,
        message: str,
        schedule: datetime = None,
    ):
        await self.ensure_connected()

        extension = os.path.splitext(photo_name)[1]
        with NamedTemporaryFile(suffix=extension) as temp:
            temp.write(photo.read())
            temp.flush()
            await self.client.send_file(
                chat_id,
                temp.name,
                caption=message,
                schedule=schedule,
            )

    async def get_chats(self, limit: int) -> list[dict]:
        await self.ensure_connected()

        chats = []

        async for chat in self.client.iter_dialogs(limit=limit):
            chats.append(
                {
                    "id": chat.id,
                    "name": chat.name,
                }
            )

        return chats

    async def get_last_scheduled_message_date(
        self, chat_id: Union[str, int]
    ) -> Optional[datetime]:
        await self.ensure_connected()

        async for msg in self.client.iter_messages(
            chat_id, reverse=False, scheduled=True, limit=1
        ):
            if not msg.message:
                continue

            return msg.date

        return None
