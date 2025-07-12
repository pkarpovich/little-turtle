from datetime import timezone, timedelta, datetime
from os.path import basename
from typing import BinaryIO

from aiogram import Bot, Router, F
from aiogram.types import CallbackQuery, Message

from little_turtle.constants import Reactions, ReplyKeyboardItems
from little_turtle.controlles import StoriesController
from little_turtle.handlers.middlewares import BotContext
from little_turtle.handlers.routers.actions import ForwardAction, ForwardCallback
from little_turtle.handlers.routers.base import BaseStoriesRouter
from little_turtle.services import AppConfig, LoggerService, TelegramService


class CallbackQueryHandlerRouter(BaseStoriesRouter):
    def __init__(
        self,
        bot: Bot,
        story_controller: StoriesController,
        config_service: AppConfig,
        logger_service: LoggerService,
        telegram_service: TelegramService,
    ):
        super().__init__(bot, story_controller, config_service)

        self.config = config_service
        self.logger_service = logger_service
        self.telegram_service = telegram_service

    def get_router(self) -> Router:
        regenerate_filter = F.action.in_(
            {
                ForwardAction.REGENERATE_STORY,
                ForwardAction.REGENERATE_IMAGE,
            }
        )
        self.router.callback_query(ForwardCallback.filter(regenerate_filter))(
            self.regenerate_query_handler
        )

        set_filter = F.action.in_(
            {
                ForwardAction.SET_STORY,
                ForwardAction.SET_IMAGE,
                ForwardAction.SET_DATE,
            }
        )
        self.router.callback_query(ForwardCallback.filter(set_filter))(
            self.set_query_handler
        )

        topic_filter = F.action == ForwardAction.SELECT_TARGET_TOPIC
        self.router.callback_query(ForwardCallback.filter(topic_filter))(
            self.set_topic_handler
        )

        schedule_filter = F.action == ForwardAction.SCHEDULE
        self.router.callback_query(ForwardCallback.filter(schedule_filter))(
            self.schedule_new_story
        )

        self.router.message()(self.sticker_action_handler)

        return self.router

    async def regenerate_query_handler(
        self, query: CallbackQuery, callback_data: ForwardCallback, ctx: BotContext
    ):
        await query.answer("Generating...")
        msg = query.message

        match callback_data.action:
            case ForwardAction.REGENERATE_STORY:
                await self.async_generate_action(ctx, self.generate_story)


            case ForwardAction.REGENERATE_IMAGE:
                await self.async_generate_action(ctx, self.generate_image)

        await self.set_message_reaction(
            msg.chat.id, msg.message_id, Reactions.SALUTE_FACE
        )

    async def set_query_handler(
        self, query: CallbackQuery, callback_data: ForwardCallback, ctx: BotContext
    ):
        msg = query.message

        match callback_data.action:
            case ForwardAction.SET_DATE:
                await ctx.state.update_data(date=msg.text)

            case ForwardAction.SET_STORY:
                await ctx.state.update_data(story=msg.text)


            case ForwardAction.SET_IMAGE:
                image_path = await self.save_file_to_disk(msg.photo[-1].file_id)

                await ctx.state.update_data(image=image_path)

        await self.set_message_reaction(msg.chat.id, msg.message_id, Reactions.LIKE)
        await query.answer("Done!")

    async def set_topic_handler(
        self, query: CallbackQuery, callback_data: ForwardCallback, ctx: BotContext
    ):
        topics = query.message.text.split("\n\n")
        topic = topics[int(callback_data.payload) - 1]

        await self.set_target_topic(topic, ctx)
        await self.set_message_reaction(
            query.message.chat.id, query.message.message_id, Reactions.LIKE
        )
        await query.answer("Done!")

    async def sticker_action_handler(self, _: Message, ctx: BotContext):
        match ctx.message.text:
            case ReplyKeyboardItems.STORY.value:
                await self.async_generate_action(ctx, self.generate_story)


            case ReplyKeyboardItems.IMAGE.value:
                await self.async_generate_action(ctx, self.generate_image)

            case ReplyKeyboardItems.PREVIEW.value:
                await self.preview_story(ctx)

    async def schedule_new_story(self, query: CallbackQuery, ctx: BotContext):
        state = await ctx.state.get_data()

        text = state.get("story")
        date = await self.__prepare_schedule_date(state.get("date"))
        photo, photo_name = await self.__get_file(query.message.photo[-1].file_id)

        for chat_id in self.config.CHAT_IDS_TO_SEND_STORIES:
            self.logger_service.info(
                "Sending scheduled story",
                chat_id=chat_id,
                date=date,
            )
            await self.telegram_service.send_photo(
                chat_id,
                photo,
                photo_name,
                text,
                date,
            )
            photo.seek(0)

        await self.set_message_reaction(
            ctx.message.chat.id, ctx.message.message_id, Reactions.LIKE
        )
        await query.answer("Done!")
        await ctx.state.clear()

    async def __get_file(self, file_id: str) -> [BinaryIO, str]:
        file = await self.bot.get_file(file_id)
        return await self.bot.download_file(file.file_path), basename(file.file_path)

    async def __prepare_schedule_date(self, date: str) -> datetime | None:
        try:
            tz = timezone(timedelta(hours=self.config.DEFAULT_TZ))

            date_obj = datetime.strptime(date, "%d.%m.%Y")
            return date_obj.replace(
                hour=self.config.DEFAULT_SCHEDULE_HOUR,
                minute=self.config.DEFAULT_SCHEDULE_MINUTE,
                second=self.config.DEFAULT_SCHEDULE_SECOND,
                tzinfo=tz,
            )

        except (ValueError, IndexError):
            return None
