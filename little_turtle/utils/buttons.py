from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def prepare_buttons(buttons: dict[str, CallbackData]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    for key, value in buttons.items():
        builder.add(InlineKeyboardButton(
            text=key,
            callback_data=value.pack()
        ))

    row_lengths = split_buttons_to_rows(list(buttons.keys()))
    builder.adjust(*row_lengths)

    return builder.as_markup()


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
