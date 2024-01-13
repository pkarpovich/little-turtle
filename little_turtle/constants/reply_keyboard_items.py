from enum import Enum


class ReplyKeyboardItems(Enum):
    STORY: str = "📜"
    IMAGE_PROMPT: str = "🎨"
    IMAGE: str = "🖼️"
    STATE: str = "🐢"
    PREVIEW: str = "📲"
    CANCEL: str = "❌"
