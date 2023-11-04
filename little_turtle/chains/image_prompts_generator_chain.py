from typing import TypedDict

from langchain.chains import LLMChain
from langchain.chains.base import Chain
from langchain.prompts import PromptTemplate
from langchain.schema.language_model import BaseLanguageModel

from little_turtle.chains import ChainAnalytics
from little_turtle.prompts import IMAGE_PROMPTS_GENERATOR_PROMPT
from little_turtle.services import AppConfig


class ImagePromptsGeneratorChainVariables(TypedDict):
    model_version: str
    new_story: str


class ImagePromptsGeneratorChain:
    llm_chain: Chain = None

    def __init__(self, llm: BaseLanguageModel, chain_analytics: ChainAnalytics, config: AppConfig):
        self.config = config
        self.chain_analytics = chain_analytics
        self.llm_chain = LLMChain(
            prompt=PromptTemplate.from_template(IMAGE_PROMPTS_GENERATOR_PROMPT),
            llm=llm,
            verbose=config.DEBUG,
        )

    def run(self, variables: ImagePromptsGeneratorChainVariables) -> str:
        image_prompt = self.llm_chain.run(variables, callbacks=[self.chain_analytics.callback_handler])
        self.chain_analytics.flush()

        return image_prompt

    def enrich_run_variables(self, content: str) -> ImagePromptsGeneratorChainVariables:
        return ImagePromptsGeneratorChainVariables(
            model_version=self.config.IMAGE_GEN_MODEL_VERSION,
            new_story=content,
        )
