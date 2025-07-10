from datetime import datetime
from typing import TypedDict, List
from pydantic import BaseModel, Field
from prompt_template import PromptTemplate

from little_turtle.services import AppConfig
from little_turtle.llm_provider import LLMClient

template = PromptTemplate("""
You are a Content Curator for a book, tasked with searching for and curating historical events that occurred on a specific day. Follow these instructions carefully:

1. You will be provided with a specific date in the format "day month" (e.g., "15 March", "4 July"). The date is:
<date>
${date}
</date>

2. Use a web search tool to find historical events that happened on the provided date. (Note: In this instruction set, we assume you have access to such a tool. If you don't, please inform the user that you need web search capabilities to complete this task.)

3. From your search results, filter OUT events that are:
   - Related to politics with impact only on a specific country
   - Connected to religion or religious holidays
   - Negative events (wars, disasters, tragedies, deaths)
   - Not visually engaging or difficult to illustrate

4. Select and rank events based on these criteria:
   - Visual appeal (events that are easy to illustrate should rank higher)
   - Universal human interest and engagement
   - Positive impact on human history and progress
   - Scientific discoveries, cultural milestones, exploration achievements

5. Present exactly 5 events in the following language:
<language>
${language}
</language>
If the events are not already in ${language}, translate them accurately.

6. For each event, include:
   - The year it occurred
   - A concise, engaging description (2-3 sentences maximum)
   - Focus on the "why it matters" aspect

7. After finding and filtering the events, use the record_historical_events tool to provide your final curated list of exactly 5 events.

8. Each event in the events array should be a single string containing:
   - The year it occurred
   - A colon and space
   - The event description and its significance

Example format for each event:
"1876: Alexander Graham Bell patents the telephone. This invention revolutionized long-distance communication, paving the way for modern telecommunications."

Remember to adhere to the filtering and selection criteria, and ensure that all events are presented in ${language}.
""")

class HistoricalEvents(BaseModel):
    events: list[str] = Field(description="List of historical events for a specific day")

class HistoricalEventsChainVariables(TypedDict):
    events: List[str]
    language: str


class HistoricalEventsChain:
    def __init__(self, config: AppConfig, llm_client: LLMClient):
        self.config = config
        self.llm_client = llm_client

    def run(self, date_string: str) -> HistoricalEvents:
        date_object = datetime.strptime(date_string, "%d.%m.%Y")
        formatted_date = date_object.strftime("%d %B")
        
        instructions = template.to_string(
            language=self.config.GENERATION_LANGUAGE,
            date=formatted_date,
        )

        messages = [
            {"role": "system", "content": instructions},
            {
                "role": "user",
                "content": f"Find historical events that happened on {formatted_date}. "
                           "Please provide the events in the specified language.",
            }
        ]
        
        resp = self.llm_client.create_completion_with_tools(
            messages=messages,
            tools=[
                {
                    "type": "web_search_20250305",
                    "name": "web_search",
                    "max_uses": 5
                },
                {
                    "name": "record_historical_events",
                    "description": "Record the curated list of historical events for the specified date",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "events": {
                                "type": "array",
                                "items": {
                                    "type": "string",
                                    "description": "A historical event with year and description"
                                },
                                "description": "List of historical events for a specific day"
                            }
                        },
                        "required": ["events"]
                    }
                }
            ],
            max_tokens=1024,
        )

        if hasattr(resp.raw_response, 'content'):
            for content in resp.raw_response.content:
                if content.type == "tool_use" and content.name == "record_historical_events":
                    return HistoricalEvents(**content.input)
        
        raise ValueError("No structured output found in response")
