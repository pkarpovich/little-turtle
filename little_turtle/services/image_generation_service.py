from typing import TypedDict, TYPE_CHECKING

from midjourney_api import TNL

if TYPE_CHECKING:
    from little_turtle.services import AppConfig, LoggerService


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
    def __init__(self, config: 'AppConfig', logger_service: 'LoggerService'):
        self.logger_service = logger_service
        self.tnl = TNL(config.TNL_API_KEY)

    def imagine(self, text: str) -> ImageRequestStatus:
        image_request_status = self.tnl.imagine(text)
        self.logger_service.info("Imagining image", image_request_status=image_request_status, text=text)
        return image_request_status

    def get_image(self, message_id: str) -> ImageStatus:
        image = self.tnl.get_message_and_progress(message_id, 60)
        self.logger_service.info("Retrieving image status", message_id=message_id, image_status=image)

        return image

    def trigger_button(self, button: str, message_id: str) -> ImageRequestStatus:
        image_request_status = self.tnl.button(button, message_id)
        self.logger_service.info("Triggering button", image_request_status=image_request_status, button=button,
                                 message_id=message_id)
        return image_request_status
