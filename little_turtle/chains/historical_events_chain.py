from datetime import datetime

from openai.types.responses import WebSearchToolParam
from typing import TypedDict, List
from pydantic import BaseModel, Field
from openai import OpenAI
from prompt_template import PromptTemplate

from little_turtle.services import AppConfig

template = PromptTemplate("""
You are a Content Curator for a book. Your task is to search historical events for specific day. Please follow these steps:

Step 1:
Remove the events from the list based on the following criteria:
- Events that related to politics, that has impact only on a specific country
- Events that connected to religion or religious holidays
- Negative events for human history, such as wars, disasters and tragedies
- Events that are not visually engaging

Step 2:
Sort events by following criteria:
- Events that easy to visualize should be first
- Most engaging events should be at the top of the list
- Events that influence to the human history should be at the top of the list

Step 3:
Result language should be ${language}. Avoid adding any additional information to the event information

Show the top 5 events for the specific day:
""")

class HistoricalEvents(BaseModel):
    events: list[str] = Field(description="List of historical events for a specific day")

class HistoricalEventsChainVariables(TypedDict):
    events: List[str]
    language: str


class HistoricalEventsChain:
    def __init__(self, config: AppConfig):
        self.config = config
        # TODO: replace with generic language model class
        self.client = OpenAI()

    def run(self, date_string: str) -> HistoricalEvents:
        instructions = template.to_string(language=self.config.GENERATION_LANGUAGE)

        date_object = datetime.strptime(date_string, "%d.%m.%Y")
        formatted_date = date_object.strftime("%d %B")

        resp = self.client.responses.parse(
            model="gpt-4.1",
            tools=[WebSearchToolParam(type="web_search_preview", search_context_size="low")],
            instructions=instructions,
            input=f"Day: {formatted_date}",
            text_format=HistoricalEvents,
            temperature=0.8,
        )

        return resp.output_parsed
