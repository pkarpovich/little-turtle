import asyncio

from dependency_injector.wiring import inject, Provide
from dotenv import load_dotenv

from little_turtle.container import Container
from little_turtle.handlers import TelegramHandlers


@inject
async def main(
        telegram_handler: TelegramHandlers = Provide[Container.telegram_handlers],
):
    telegram_handler.run()


if __name__ == "__main__":
    load_dotenv()

    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
