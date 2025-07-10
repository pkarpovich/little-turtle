from openai.types import Reasoning
from typing import TypedDict, List

from openai import OpenAI
from langchain.base_language import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from little_turtle.chains import ChainAnalytics
from little_turtle.prompts import TURTLE_STORY_PROMPT_TEMPLATE
from little_turtle.services import AppConfig
from little_turtle.utils import get_day_of_week


class TurtleStoryChainVariables(TypedDict):
    date: str
    comment: str
    language: str
    target_topics: List[str]


class TurtleStoryChain:
    def __init__(
        self, llm: BaseLanguageModel, chain_analytics: ChainAnalytics, config: AppConfig
    ):
        self.config = config
        self.client = OpenAI()

    def run(self, target_topics: str) -> str:
        instructions = TURTLE_STORY_PROMPT_TEMPLATE.to_string(language=self.config.GENERATION_LANGUAGE, current_date=target_topics['date'])
        resp = self.client.responses.create(
            model='o4-mini',
            reasoning=Reasoning(effort="medium"),
            instructions=instructions,
            input=target_topics['target_topics'][0],
        )


        return resp.output_text

    def enrich_run_variables(
        self,
        date: str,
        target_topics: List[str],
    ) -> TurtleStoryChainVariables:
        return TurtleStoryChainVariables(
            target_topics=target_topics,
            date=f"{date} ({get_day_of_week(date)})",
            language=self.config.GENERATION_LANGUAGE,
        )
