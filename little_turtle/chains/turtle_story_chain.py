from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain

from little_turtle.prompts import TURTLE_STORY_PROMPT_TEMPLATE


class TurtleStoryChain:
    llm_chain: Chain = None

    def __init__(self, llm: BaseLanguageModel):
        self.llm_chain = LLMChain(
            prompt=PromptTemplate.from_template(TURTLE_STORY_PROMPT_TEMPLATE),
            llm=llm,
        )

    def run(self, variables: dict) -> str:
        return self.llm_chain.run(variables)
