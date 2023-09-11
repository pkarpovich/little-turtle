from little_turtle.chains import TurtleStoryChain, ImagePromptsGeneratorChain
from little_turtle.services import ImageGenerationService, ImageStatus, ImageRequestStatus
from little_turtle.stores import Story, StoryStore
from little_turtle.utils import remove_optional_last_period


class StoriesController:
    def __init__(
            self,
            story_store: StoryStore,
            story_chain: TurtleStoryChain,
            image_prompt_chain: ImagePromptsGeneratorChain,
            image_generation_service: ImageGenerationService
    ):
        self.story_store = story_store
        self.story_chain = story_chain
        self.image_prompt_chain = image_prompt_chain
        self.image_generation_service = image_generation_service

    def imagine_story(self, image_prompt: str) -> ImageRequestStatus:
        return self.image_generation_service.imagine(image_prompt)

    def get_image_status(self, message_id: str) -> ImageStatus:
        return self.image_generation_service.get_image(message_id)

    def suggest_story_prompt(self, story_content: str) -> str:
        messages = self.__get_messages_for_story()

        image_prompt_variables = ImagePromptsGeneratorChain.enrich_run_variables(story_content, messages)
        image_prompt = self.image_prompt_chain.run(image_prompt_variables)

        return remove_optional_last_period(image_prompt)

    def suggest_story(self, date) -> str:
        messages = self.__get_messages_for_story()

        story_variables = TurtleStoryChain.enrich_run_variables(date, messages)
        new_story = self.story_chain.run(story_variables)

        return new_story["content"]

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
