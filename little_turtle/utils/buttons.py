from typing import TypeVar

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

T = TypeVar('T')


def prepare_buttons(
        buttons: dict[str, CallbackData] | dict[str, None],
        builder_type: T = InlineKeyboardBuilder,
        markup_args: dict = None
) -> InlineKeyboardMarkup | ReplyKeyboardMarkup:
    builder = builder_type()
    button = InlineKeyboardButton if isinstance(builder_type(), InlineKeyboardBuilder) else KeyboardButton

    for key, value in buttons.items():
        callback_data = value.pack() if isinstance(value, CallbackData) else None

        builder.add(button(
            callback_data=callback_data,
            text=key,
        ))

    return builder.as_markup(**markup_args) if markup_args else builder.as_markup()


def split_buttons_to_rows(buttons: [str]) -> [int]:
    rows = []
    temp_row = []

    for i, button in enumerate(buttons):
        current_len = len(button)

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
