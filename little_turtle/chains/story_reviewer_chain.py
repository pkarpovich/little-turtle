from typing import TypedDict

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel

from little_turtle.prompts import STORY_REVIEWER_PROMPT_TEMPLATE
from little_turtle.services import AppConfig


class StoryReviewerChainVariables(TypedDict):
    story: str
    language: str


class StoryReviewerChain:
    def __init__(self, llm: BaseLanguageModel, config: AppConfig):
        self.llm_chain = LLMChain(
            prompt=PromptTemplate.from_template(STORY_REVIEWER_PROMPT_TEMPLATE),
            llm=llm,
            verbose=config.DEBUG,
            output_key="review",
        )

    def get_chain(self) -> LLMChain:
        return self.llm_chain

    def run(self, variables: StoryReviewerChainVariables) -> str:
        return self.llm_chain.run(variables)

    @staticmethod
    def enrich_run_variables(content: str, language: str) -> StoryReviewerChainVariables:
        return StoryReviewerChainVariables(
            story=content,
            language=language,
        )
