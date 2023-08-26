from little_turtle.chains import TurtleStoryChain, ImagePromptsGeneratorChain
from little_turtle.stores import Story, StoryStore


class StoriesController:
    story_store: StoryStore
    story_chain: TurtleStoryChain
    image_prompt_chain: ImagePromptsGeneratorChain

    def __init__(self,
                 story_store: StoryStore,
                 story_chain: TurtleStoryChain,
                 image_prompt_chain: ImagePromptsGeneratorChain
                 ):
        self.story_store = story_store
        self.story_chain = story_chain
        self.image_prompt_chain = image_prompt_chain

    def generate_story(self, date: str) -> Story:
        messages = self.story_store.get_all(
            query={
                "image_prompt": {
                    "$ne": ""
                }
            }
        )

        story_variables = TurtleStoryChain.enrich_run_variables(date, messages)
        new_story = self.story_chain.run(story_variables)

        image_prompt_variables = ImagePromptsGeneratorChain.enrich_run_variables(new_story, messages)
        image_prompt = self.image_prompt_chain.run(image_prompt_variables)

        new_story["image_prompt"] = image_prompt

        return new_story
