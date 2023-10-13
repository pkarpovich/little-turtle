from typing import TypedDict, List, Optional

from langchain.base_language import BaseLanguageModel
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

from little_turtle.prompts import TURTLE_STORY_PROMPT_TEMPLATE
from little_turtle.services import AppConfig
from little_turtle.stores import Story
from little_turtle.utils import get_day_of_week, random_pick_n


class TurtleStoryChainVariables(TypedDict):
    date: str
    language: str
    target_topics: List[str]
    stories_summary: List[str]
    message_examples: List[str]
    comment: str


class TurtleStoryChain:
    def __init__(self, llm: BaseLanguageModel, config: AppConfig):
        self.config = config
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

    def enrich_run_variables(
            self,
            date: str,
            stories: List[Story],
            target_topics: List[str],
            stories_summary: List[str],
            generation_comment: Optional[str]
    ) -> TurtleStoryChainVariables:
        picked_messages = random_pick_n(stories, 3) if len(generation_comment) == 0 else list()
        message_examples = [message["content"] for message in picked_messages]

        return TurtleStoryChainVariables(
            comment=generation_comment,
            target_topics=target_topics,
            stories_summary=stories_summary,
            message_examples=message_examples,
            date=f"{date} ({get_day_of_week(date)})",
            language=self.config.GENERATION_LANGUAGE,
        )
