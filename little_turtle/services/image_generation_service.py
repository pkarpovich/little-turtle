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
    description: str
    imageUrl: str


class ImageStatus(TypedDict):
    progress: int
    progressImageUrl: str
    response: ImageStatusResponse


class ImageGenerationService:
    def __init__(self, config: 'AppConfig', logger_service: 'LoggerService'):
        self.logger_service = logger_service
        self.config = config

    def imagine(self, text: str) -> ImageRequestStatus:
        client = self.__get_client()

        image_request_status = client.imagine(text)
        self.logger_service.info("Imagining image", image_request_status=image_request_status, text=text)
        return image_request_status

    def get_image(self, message_id: str) -> ImageStatus:
        client = self.__get_client()

        image = client.get_message_and_progress(message_id, 60)
        self.logger_service.info("Retrieving image status", message_id=message_id, image_status=image)

        return image

    def trigger_button(self, button: str, message_id: str) -> ImageRequestStatus:
        client = self.__get_client()

        image_request_status = client.button(button, message_id)
        self.logger_service.info("Triggering button", image_request_status=image_request_status, button=button,
                                 message_id=message_id)
        return image_request_status

    def __get_client(self) -> TNL:
        return TNL(self.config.TNL_API_KEY)
