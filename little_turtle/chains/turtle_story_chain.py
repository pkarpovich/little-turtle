import locale
from datetime import datetime

from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain

from little_turtle.prompts import TURTLE_STORY_PROMPT_TEMPLATE


def get_day_of_week(date: str) -> str:
    locale.setlocale(locale.LC_TIME, 'ru_RU')

    date_obj = datetime.strptime(date, '%d.%m.%Y')
    return date_obj.strftime('%A').capitalize()


def enrich_run_variables(date: str, messages: list[str]) -> dict:
    return {
        "date": f"{date} ({get_day_of_week(date)})",
        "message_example_1": messages[0],
        "message_example_2": messages[1],
        "message_example_3": messages[2],
    }


class TurtleStoryChain:
    llm_chain: Chain = None

    def __init__(self, llm: BaseLanguageModel):
        self.llm_chain = LLMChain(
            prompt=PromptTemplate.from_template(TURTLE_STORY_PROMPT_TEMPLATE),
            llm=llm,
        )

    def run(self, variables: dict) -> str:
        return self.llm_chain.run(variables)
