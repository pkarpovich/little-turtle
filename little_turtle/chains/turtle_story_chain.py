from typing import TypedDict, List

from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel

from little_turtle.prompts import TURTLE_STORY_PROMPT_TEMPLATE
from little_turtle.services import AppConfig
from little_turtle.stores import Story
from little_turtle.utils import get_day_of_week, random_pick_n


class TurtleStoryChainVariables(TypedDict):
    date: str
    message_example_1: str
    message_example_2: str
    message_example_3: str
    stories_summary: List[str]


class TurtleStoryChain:
    def __init__(self, llm: BaseLanguageModel, config: AppConfig):
        self.llm_chain = LLMChain(
            prompt=PromptTemplate.from_template(TURTLE_STORY_PROMPT_TEMPLATE, template_format="jinja2"),
            llm=llm,
            output_key="story",
            verbose=config.DEBUG,
        )

    def get_chain(self) -> LLMChain:
        return self.llm_chain

    def run(self, variables: TurtleStoryChainVariables) -> str:
        return self.llm_chain.run(variables)

    @staticmethod
    def enrich_run_variables(date: str, stories: List[Story], stories_summary: List[str]) -> TurtleStoryChainVariables:
        picked_messages = random_pick_n(stories, 3)

        return TurtleStoryChainVariables(
            date=f"{date} ({get_day_of_week(date)})",
            message_example_1=picked_messages[0]["content"],
            message_example_2=picked_messages[1]["content"],
            message_example_3=picked_messages[2]["content"],
            stories_summary=stories_summary,
        )
