from typing import TYPE_CHECKING

import sentry_sdk

if TYPE_CHECKING:
    from little_turtle.services import AppConfig, LoggerService


class ErrorHandlerService:
    def __init__(self, config: 'AppConfig', logger_service: 'LoggerService'):
        self.config = config
        self.logger_service = logger_service

    def start(self):
        if not self.config.ERROR_HANDLER_ENABLED:
            return

        self.logger_service.info("Starting error handler service")

        sentry_sdk.init(
            dsn=self.config.ERROR_HANDLER_DNS,
            environment=self.config.ERROR_HANDLER_ENVIRONMENT,
            server_name=self.config.ERROR_HANDLER_SERVER_NAME,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )
