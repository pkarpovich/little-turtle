import asyncio

from dependency_injector.wiring import inject, Provide
from dotenv import load_dotenv

from little_turtle.container import Container
from little_turtle.handlers import TelegramHandlers
from little_turtle.services import TelegramService


@inject
async def main(
        telegram_service: TelegramService = Provide[Container.telegram_service],
        telegram_handler: TelegramHandlers = Provide[Container.telegram_handlers],
):
    await telegram_service.login()
    await telegram_handler.run()


if __name__ == "__main__":
    load_dotenv()

    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
