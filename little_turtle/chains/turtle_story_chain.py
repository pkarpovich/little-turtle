from typing import TypedDict, List, Optional

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
    def __init__(self, llm: BaseLanguageModel, chain_analytics: ChainAnalytics, config: AppConfig):
        self.config = config
        self.chain_analytics = chain_analytics
        prompt = ChatPromptTemplate.from_template(TURTLE_STORY_PROMPT_TEMPLATE, template_format="jinja2")

        self.chain = prompt | llm | StrOutputParser()

    def run(self, variables: TurtleStoryChainVariables) -> str:
        return self.chain.invoke(variables, config={
            "callbacks": [self.chain_analytics.get_callback_handler]
        })

    def enrich_run_variables(
            self,
            date: str,
            target_topics: List[str],
            generation_comment: Optional[str]
    ) -> TurtleStoryChainVariables:
        return TurtleStoryChainVariables(
            comment=generation_comment,
            target_topics=target_topics,
            date=f"{date} ({get_day_of_week(date)})",
            language=self.config.GENERATION_LANGUAGE,
        )
