# from langfuse.callback import CallbackHandler
from little_turtle.services import AppConfig


class ChainAnalytics:
    # callback_handler: CallbackHandler

    def __init__(self, config: AppConfig):
        self.config = config
        # self.callback_handler = CallbackHandler(
        #     config.LANGFUSE_PUBLIC_KEY,
        #     config.LANGFUSE_SECRET_KEY,
        #     config.LANGFUSE_URL
        # )

    @property
    def get_callback_handler(self):
        # return self.callback_handler
        return None

    def flush(self) -> None:
        # self.callback_handler.langfuse.flush()
        return None

