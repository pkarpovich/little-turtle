from datetime import timedelta, datetime
from typing import TypedDict, List

from little_turtle.chains import (
    HistoricalEventsChain,
    ImageGeneratorChain,
    TurtleStoryChain,
)
from little_turtle.chains.historical_events_chain import HistoricalEvents, HistoricalEventsChainVariables
from little_turtle.chains.turtle_story_chain import TurtleStoryChainVariables
from little_turtle.chains.image_generator_chain import ImageGeneratorChainVariables
from little_turtle.services import AppConfig, TelegramService
from little_turtle.utils import remove_optional_last_period, get_day_of_week


class StoryResponse(TypedDict):
    story: str
    review: str
    story_event_summary: str


class StoriesController:
    def __init__(
        self,
        config: AppConfig,
        story_chain: TurtleStoryChain,
        image_generator_chain: ImageGeneratorChain,
        historical_events_chain: HistoricalEventsChain,
        telegram_service: TelegramService,
    ):
        self.config = config
        self.story_chain = story_chain
        self.historical_events_chain = historical_events_chain
        self.image_generator_chain = image_generator_chain
        self.telegram_service = telegram_service

    def suggest_on_this_day_events(self, date: str) -> HistoricalEvents:
        date_object = datetime.strptime(date, "%d.%m.%Y")
        formatted_date = date_object.strftime("%d %B")

        return self.historical_events_chain.run(
            HistoricalEventsChainVariables(
                language=self.config.GENERATION_LANGUAGE,
                date=formatted_date,
            )
        )

    def imagine_story(self, story: str) -> str:
        return self.image_generator_chain.run(
            ImageGeneratorChainVariables(
                story=story,
            )
        )


    def suggest_story(
        self,
        date: str,
        target_topics: List[str],
    ) -> str:
        return self.story_chain.run(
            TurtleStoryChainVariables(
                current_date=f"{date} ({get_day_of_week(date)})",
                language=self.config.GENERATION_LANGUAGE,
                historical_event=target_topics[0],
            )
        )

    async def get_next_story_date(self) -> str:
        last_scheduled_story_date = (
            await self.telegram_service.get_last_scheduled_message_date(
                self.config.CHAT_IDS_TO_SEND_STORIES[0]
            )
            or datetime.now()
        )

        raw_next_story_date = last_scheduled_story_date + timedelta(days=1)
        return raw_next_story_date.strftime("%d.%m.%Y")
