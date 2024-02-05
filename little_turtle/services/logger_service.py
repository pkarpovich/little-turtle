import logging
import os

import structlog
from structlog.dev import ConsoleRenderer
from structlog.processors import JSONRenderer


def get_renderer() -> JSONRenderer | ConsoleRenderer:
    if os.environ.get("DEV_LOGS", False):
        return ConsoleRenderer()
    return JSONRenderer()


class LoggerService:
    def __init__(self):
        timestamper = structlog.processors.TimeStamper(fmt="iso", utc=True)

        structlog_processors = [
            structlog.stdlib.add_log_level,
            structlog.processors.add_log_level,
            structlog.contextvars.merge_contextvars,
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.dev.set_exc_info,
            timestamper,
        ]

        structlog.configure(
            processors=structlog_processors + [get_renderer()],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.PrintLoggerFactory(),
            cache_logger_on_first_use=False,
        )

        logs_level = os.environ.get("LOGS_LEVEL", "INFO")

        if logs_level == "INFO":
            logging.basicConfig(level=logging.INFO)

        self.logger = structlog.get_logger()

    def info(self, message: str, **kwargs):
        self.logger.info(message, **kwargs)

    def error(self, message: str, **kwargs):
        self.logger.error(message, **kwargs)
