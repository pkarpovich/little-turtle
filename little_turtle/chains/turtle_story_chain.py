import locale
import random
from datetime import datetime

from langchain import LLMChain, PromptTemplate
from langchain.base_language import BaseLanguageModel
from langchain.chains.base import Chain

from little_turtle.prompts import TURTLE_STORY_PROMPT_TEMPLATE
from little_turtle.stores import Story


def get_day_of_week(date: str) -> str:
    locale.setlocale(locale.LC_TIME, 'ru_RU')

    date_obj = datetime.strptime(date, '%d.%m.%Y')
    return date_obj.strftime('%A').capitalize()


def enrich_run_variables(date: str, stories: list[Story]) -> dict:
    picked_messages = random.sample(
        list(
            map(lambda story: story["content"], stories)
        ),
        3
    )

    return {
        "date": f"{date} ({get_day_of_week(date)})",
        "message_example_1": picked_messages[0],
        "message_example_2": picked_messages[1],
        "message_example_3": picked_messages[2],
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
