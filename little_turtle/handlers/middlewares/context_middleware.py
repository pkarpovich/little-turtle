from dataclasses import dataclass
from typing import Callable, Dict, Any, Awaitable

from aiogram.fsm.context import FSMContext
from aiogram.types import Update, Message


@dataclass
class BotContext:
    state: FSMContext
    message: Message
    chat_id: int
    user_id: int


async def context_middleware(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
):
    dispatcher = data["dispatcher"]
    bot = data["bot"]

    msg_context = event.message if event.message else event.callback_query.message

    chat_id = msg_context.chat.id
    user_id = msg_context.from_user.id
    state = dispatcher.fsm.get_context(bot, chat_id, chat_id)

    data["ctx"] = BotContext(
        message=msg_context,
        user_id=user_id,
        chat_id=chat_id,
        state=state,
    )

    return await handler(event, data)
