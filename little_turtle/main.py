import asyncio

from dependency_injector.wiring import inject, Provide
from dotenv import load_dotenv

from little_turtle.container import Container
from little_turtle.handlers import TelegramHandlers
from little_turtle.handlers.routers import CallbackQueryHandlerRouter, SystemRouter, SetStateRouter, AdminCommandsRouter
from little_turtle.services import ErrorHandlerService


@inject
async def main(
        callback_query_handler_router: CallbackQueryHandlerRouter = Provide[Container.callback_query_handler_router],
        error_handler_service: ErrorHandlerService = Provide[Container.error_handler_service],
        admin_commands_router: AdminCommandsRouter = Provide[Container.admin_commands_router],
        telegram_handler: TelegramHandlers = Provide[Container.telegram_handlers],
        set_state_router: SetStateRouter = Provide[Container.set_state_router],
        system_router: SystemRouter = Provide[Container.system_router],
):
    error_handler_service.start()
    telegram_handler.init_routers(
        system_router,
        set_state_router,
        admin_commands_router,
        callback_query_handler_router

    )
    await telegram_handler.run()


if __name__ == "__main__":
    load_dotenv()

    container = Container()
    container.init_resources()
    container.wire(modules=[__name__])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main())
