from typing import TypedDict, List

from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.language_model import BaseLanguageModel

from little_turtle.services import AppConfig

DAY_EVENT_PICKER_PROMPT = """
You are a Content Curator for a children's book. Your task is to select the event of the day from a provided list of events. Please follow these steps:

Step 1:
You should exclude political, war-related, and other sensitive events. The target audience is children.
Therefore, you should select only positive events. The event should be interesting and visually engaging to easily illustrate it within a story.

Step 2:
Sort events by interest and select the top 5 events.

Step 3:
Translate events into {language}. Avoid adding any additional information to the event information

Events:
{% for event in events %}
{{ event }}
{% endfor %}

The result should be a list of five events, each separated by two new lines. Refrain from displaying any intermediate information
"""


class HistoricalEventsChainVariables(TypedDict):
    events: List[str]
    language: str


class HistoricalEventsChain:
    def __init__(self, llm: BaseLanguageModel, config: AppConfig):
        self.config = config
        prompt = ChatPromptTemplate.from_template(DAY_EVENT_PICKER_PROMPT, template_format="jinja2")

        self.chain = prompt | llm | StrOutputParser()

        self.llm_chain = LLMChain(
            prompt=PromptTemplate.from_template(DAY_EVENT_PICKER_PROMPT, template_format="jinja2"),
            llm=llm,
            verbose=config.DEBUG
        )

    def run(self, variables: HistoricalEventsChainVariables) -> str:
        return self.chain.invoke(variables)

    def enrich_run_variables(self, events: List[str]) -> HistoricalEventsChainVariables:
        return HistoricalEventsChainVariables(
            language=self.config.GENERATION_LANGUAGE,
            events=[event for event in events],
        )
