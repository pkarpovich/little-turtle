from datetime import timedelta, datetime
from typing import TypedDict, List

from little_turtle.agents import (
    HistoricalEventsAgent,
    ImageAgent,
    StoryAgent,
)
from little_turtle.agents.historical_events_agent import (
    HistoricalEvents,
    HistoricalEventsAgentVariables,
)
from little_turtle.agents.story_agent import StoryAgentVariables
from little_turtle.agents.image_agent import ImageAgentVariables
from little_turtle.app_config import AppConfig
from little_turtle.services import TelegramService
from little_turtle.utils import get_day_of_week


class StoryResponse(TypedDict):
    story: str
    review: str
    story_event_summary: str


class StoriesController:
    def __init__(
        self,
        config: AppConfig,
        story_agent: StoryAgent,
        image_agent: ImageAgent,
        historical_events_agent: HistoricalEventsAgent,
        telegram_service: TelegramService,
    ):
        self.config = config
        self.story_agent = story_agent
        self.historical_events_agent = historical_events_agent
        self.image_agent = image_agent
        self.telegram_service = telegram_service

    def suggest_on_this_day_events(self, date: str) -> HistoricalEvents:
        date_object = datetime.strptime(date, "%d.%m.%Y")
        formatted_date = date_object.strftime("%d %B")

        return self.historical_events_agent.run(
            HistoricalEventsAgentVariables(
                language=self.config.GENERATION_LANGUAGE,
                date=formatted_date,
            )
        )

    def imagine_story(self, story: str) -> str:
        return self.image_agent.run(
            ImageAgentVariables(
                story=story,
            )
        )

    def suggest_story(
        self,
        date: str,
        target_topics: List[str],
    ) -> str:
        return self.story_agent.run(
            StoryAgentVariables(
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
