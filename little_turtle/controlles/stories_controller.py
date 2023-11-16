from typing import TypedDict, List, Optional

from langchain.chains import SequentialChain

from little_turtle.chains import (
    ImagePromptsGeneratorChain,
    StorySummarizationChain,
    HistoricalEventsChain,
    ImageGeneratorChain,
    StoryReviewerChain,
    TurtleStoryChain,
    ChainAnalytics,
)
from little_turtle.services import AppConfig, HistoricalEventsService
from little_turtle.stores import Story, StoryStore
from little_turtle.utils import remove_optional_last_period


class StoryResponse(TypedDict):
    story: str
    review: str
    story_event_summary: str


class StoriesController:
    def __init__(
            self,
            config: AppConfig,
            story_store: StoryStore,
            story_chain: TurtleStoryChain,
            chain_analytics: ChainAnalytics,
            story_reviewer_chain: StoryReviewerChain,
            image_generator_chain: ImageGeneratorChain,
            historical_events_chain: HistoricalEventsChain,
            image_prompt_chain: ImagePromptsGeneratorChain,
            story_summarization_chain: StorySummarizationChain,
            historical_events_service: HistoricalEventsService,
    ):
        self.config = config
        self.story_store = story_store
        self.story_chain = story_chain
        self.historical_events_chain = historical_events_chain
        self.chain_analytics = chain_analytics
        self.image_prompt_chain = image_prompt_chain
        self.story_reviewer_chain = story_reviewer_chain
        self.image_generator_chain = image_generator_chain
        self.story_summarization_chain = story_summarization_chain
        self.historical_events_service = historical_events_service

    def suggest_on_this_day_events(self, date: str) -> str:
        events = self.historical_events_service.get_by_date(date)

        return self.historical_events_chain.run(
            self.historical_events_chain.enrich_run_variables(
                events
            )
        )

    def imagine_story(self, image_prompt: str) -> str:
        return self.image_generator_chain.run(image_prompt)

    def suggest_story_prompt(self, story_content: str) -> str:
        image_prompt_variables = self.image_prompt_chain.enrich_run_variables(story_content)
        image_prompt = self.image_prompt_chain.run(image_prompt_variables)

        return remove_optional_last_period(image_prompt)

    def suggest_story(
            self,
            date: str,
            stories_summary: List[str],
            target_topics: List[str],
            generation_comment: Optional[str]
    ) -> StoryResponse:
        messages = self.__get_messages_for_story()
        story_variables = self.story_chain.enrich_run_variables(
            date,
            messages,
            target_topics,
            stories_summary,
            generation_comment
        )

        sequential_chain = SequentialChain(
            chains=[
                self.story_chain.get_chain(),
                self.story_summarization_chain.get_chain(),
                self.story_reviewer_chain.get_chain(),
            ],
            input_variables=['date', 'message_examples', 'stories_summary', 'target_topics', 'language', 'comment'],
            output_variables=['story', 'story_event_summary', 'review'],
            verbose=self.config.DEBUG,
        )

        resp = sequential_chain(story_variables, callbacks=[self.chain_analytics.get_callback_handler])
        self.chain_analytics.flush()

        return resp

    def __get_messages_for_story(self) -> list[Story]:
        return self.story_store.get_all(
            query={
                "image_prompt": {
                    "$ne": ""
                }
            }
        )
