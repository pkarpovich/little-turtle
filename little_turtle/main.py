import asyncio

from dependency_injector.wiring import inject, Provide
from dotenv import load_dotenv

from little_turtle.container import Container
from little_turtle.handlers import TelegramHandlers
from little_turtle.services import ErrorHandlerService


@inject
async def main(
        error_handler_service: ErrorHandlerService = Provide[Container.error_handler_service],
        telegram_handler: TelegramHandlers = Provide[Container.telegram_handlers],
):
    error_handler_service.start()
    await telegram_handler.run()


if __name__ == "__main__":
    print('cache test')
    load_dotenv()

    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
