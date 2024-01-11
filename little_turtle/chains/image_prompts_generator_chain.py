from typing import TypedDict

from langchain.chains.base import Chain
from langchain.schema.language_model import BaseLanguageModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from little_turtle.chains import ChainAnalytics
from little_turtle.prompts import IMAGE_PROMPTS_GENERATOR_PROMPT
from little_turtle.services import AppConfig


class ImagePromptsGeneratorChainVariables(TypedDict):
    new_story: str


class ImagePromptsGeneratorChain:
    llm_chain: Chain = None

    def __init__(self, llm: BaseLanguageModel, chain_analytics: ChainAnalytics, config: AppConfig):
        self.config = config
        self.chain_analytics = chain_analytics
        prompt = ChatPromptTemplate.from_template(IMAGE_PROMPTS_GENERATOR_PROMPT)

        self.chain = prompt | llm | StrOutputParser()

    def run(self, variables: ImagePromptsGeneratorChainVariables) -> str:
        image_prompt = self.chain.invoke(variables, config={
            "callbacks": [self.chain_analytics.get_callback_handler]
        })
        self.chain_analytics.flush()

        return image_prompt

    @staticmethod
    def enrich_run_variables(content: str) -> ImagePromptsGeneratorChainVariables:
        return ImagePromptsGeneratorChainVariables(new_story=content)
