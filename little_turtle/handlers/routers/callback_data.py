from enum import Enum
from typing import Optional

from aiogram.filters.callback_data import CallbackData


class ForwardAction(str, Enum):
    REGENERATE_STORY = "regenerate_story"
    REGENERATE_IMAGE_PROMPT = "regenerate_image_prompt"
    REGENERATE_IMAGE = "regenerate_image"
    SET_DATE = "set_date"
    SET_STORY = "set_story"
    SET_IMAGE_PROMPT = "set_image_prompt"
    SET_IMAGE = "set_image"
    SCHEDULE = "schedule"
    TARGET_TOPIC = "target_topic"
    SELECT_TARGET_TOPIC = "select_target_topic"


class ForwardCallback(CallbackData, prefix="turtle_forward"):
    action: ForwardAction
    payload: Optional[str] = None
