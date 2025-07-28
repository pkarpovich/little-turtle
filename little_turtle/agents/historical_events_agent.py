from typing import TypedDict
from pydantic import BaseModel, Field

from little_turtle.prompts.prompts_provider import PromptsProvider
from little_turtle.llm_provider import LLMClient

RECORD_HISTORICAL_EVENTS_TOOL = "record_historical_events"


class HistoricalEvents(BaseModel):
    events: list[str] = Field(description="List of historical events for a specific day")

class HistoricalEventsAgentVariables(TypedDict):
    language: str
    date: str


def get_structured_output_tool() -> dict[str, any]:
    return {
        "name": RECORD_HISTORICAL_EVENTS_TOOL,
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


def extract_structured_output(response) -> HistoricalEvents:
    if hasattr(response.raw_response, 'content'):
        for content in response.raw_response.content:
            if content.type == "tool_use" and content.name == RECORD_HISTORICAL_EVENTS_TOOL:
                return HistoricalEvents(**content.input)
    
    raise ValueError("No structured output found in response")


class HistoricalEventsAgent:
    def __init__(self, llm_client: LLMClient, prompts_provider: PromptsProvider):
        self.prompts_provider = prompts_provider
        self.llm_client = llm_client


    def run(self, prompt_vars: HistoricalEventsAgentVariables) -> HistoricalEvents:
        search_tool = self.llm_client.get_search_tool()
        resp = self.llm_client.create_completion_with_tools(
            tools=[search_tool, get_structured_output_tool()],
            **self.prompts_provider.format("little_turtle_historical_events", prompt_vars),
        )

        return extract_structured_output(resp)
