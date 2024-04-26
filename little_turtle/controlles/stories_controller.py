from datetime import timedelta, datetime
from typing import TypedDict, List

from little_turtle.chains import (
    ImagePromptsGeneratorChain,
    HistoricalEventsChain,
    ImageGeneratorChain,
    TurtleStoryChain,
)
from little_turtle.services import AppConfig, HistoricalEventsService, TelegramService
from little_turtle.utils import remove_optional_last_period


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
        image_prompt_chain: ImagePromptsGeneratorChain,
        historical_events_service: HistoricalEventsService,
        telegram_service: TelegramService,
    ):
        self.config = config
        self.story_chain = story_chain
        self.historical_events_chain = historical_events_chain
        self.image_prompt_chain = image_prompt_chain
        self.image_generator_chain = image_generator_chain
        self.historical_events_service = historical_events_service
        self.telegram_service = telegram_service

    def suggest_on_this_day_events(self, date: str) -> str:
        events = self.historical_events_service.get_by_date(date)

        return self.historical_events_chain.run(
            self.historical_events_chain.enrich_run_variables(events)
        )

    def imagine_story(self, image_prompt: str) -> str:
        return self.image_generator_chain.run(image_prompt)

    def suggest_story_prompt(self, story_content: str) -> str:
        image_prompt_variables = self.image_prompt_chain.enrich_run_variables(
            story_content
        )
        image_prompt = self.image_prompt_chain.run(image_prompt_variables)

        return remove_optional_last_period(image_prompt)

    def suggest_story(
        self,
        date: str,
        target_topics: List[str],
    ) -> str:
        return self.story_chain.run(
            self.story_chain.enrich_run_variables(
                date,
                target_topics,
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
