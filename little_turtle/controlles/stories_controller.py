from typing import TypedDict, List, Optional

from langchain.chains import SequentialChain

from little_turtle.chains import (
    ImagePromptsGeneratorChain,
    StorySummarizationChain,
    StoryReviewerChain,
    TurtleStoryChain,
)
from little_turtle.services import ImageGenerationService, ImageStatus, ImageRequestStatus, AppConfig
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
            story_reviewer_chain: StoryReviewerChain,
            image_prompt_chain: ImagePromptsGeneratorChain,
            image_generation_service: ImageGenerationService,
            story_summarization_chain: StorySummarizationChain,
    ):
        self.config = config
        self.story_store = story_store
        self.story_chain = story_chain
        self.story_reviewer_chain = story_reviewer_chain
        self.image_prompt_chain = image_prompt_chain
        self.image_generation_service = image_generation_service
        self.story_summarization_chain = story_summarization_chain

    def imagine_story(self, image_prompt: str) -> ImageRequestStatus:
        return self.image_generation_service.imagine(image_prompt)

    def get_image_status(self, message_id: str) -> ImageStatus:
        return self.image_generation_service.get_image(message_id)

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
        return sequential_chain(story_variables)

    def trigger_button(self, button: str, message_id: str) -> ImageRequestStatus:
        return self.image_generation_service.trigger_button(button, message_id)

    def __get_messages_for_story(self) -> list[Story]:
        return self.story_store.get_all(
            query={
                "image_prompt": {
                    "$ne": ""
                }
            }
        )
