from typing import TypedDict, List

from langchain import LLMChain, PromptTemplate
from langchain.chains.base import Chain
from langchain.schema.language_model import BaseLanguageModel

from little_turtle.prompts import IMAGE_PROMPTS_GENERATOR_PROMPT
from little_turtle.services import AppConfig
from little_turtle.stores import Story
from little_turtle.utils import random_pick_n


class ImagePromptsGeneratorChainVariables(TypedDict):
    prompt_example_1: str
    prompt_example_2: str
    story_example_1: str
    story_example_2: str
    new_story: str


class ImagePromptsGeneratorChain:
    llm_chain: Chain = None

    def __init__(self, llm: BaseLanguageModel, config: AppConfig):
        self.llm_chain = LLMChain(
            prompt=PromptTemplate.from_template(IMAGE_PROMPTS_GENERATOR_PROMPT),
            llm=llm,
            verbose=config.DEBUG,
        )

    def run(self, variables: ImagePromptsGeneratorChainVariables) -> str:
        return self.llm_chain.run(variables)

    @staticmethod
    def enrich_run_variables(new_story: Story, stories: List[Story]) -> ImagePromptsGeneratorChainVariables:
        picked_stories = random_pick_n(stories, 2)

        return ImagePromptsGeneratorChainVariables(
            prompt_example_1=picked_stories[0]["image_prompt"],
            prompt_example_2=picked_stories[1]["image_prompt"],
            story_example_1=picked_stories[0]["content"],
            story_example_2=picked_stories[1]["content"],
            new_story=new_story["content"],
        )
