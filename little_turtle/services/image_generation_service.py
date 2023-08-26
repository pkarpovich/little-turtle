from typing import TypedDict

from midjourney_api import TNL

from little_turtle.services import AppConfig


class ImageRequestStatus(TypedDict):
    messageId: str
    success: bool


class ImageStatusResponse(TypedDict):
    originatingMessageId: str
    buttonMessageId: str
    imageUrls: list[str]
    buttons: list[str]
    imageUrl: str


class ImageStatus(TypedDict):
    progress: int
    response: ImageStatusResponse


class ImageGenerationService:
    def __init__(self, config: AppConfig):
        self.tnl = TNL(config.TNL_API_KEY)

    def imagine(self, text: str) -> ImageRequestStatus:
        return self.tnl.imagine(text)

    def get_image(self, message_id: str) -> ImageStatus:
        return self.tnl.get_message_and_progress(message_id, 60)

    def trigger_button(self, button: str, message_id: str) -> ImageRequestStatus:
        return self.tnl.button(button, message_id)
