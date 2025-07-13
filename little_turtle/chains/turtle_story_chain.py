from typing import TypedDict, List

from little_turtle.prompts import TURTLE_STORY_PROMPT_TEMPLATE
from little_turtle.services import AppConfig
from little_turtle.llm_provider import LLMClient
from little_turtle.utils import get_day_of_week


class TurtleStoryChainVariables(TypedDict):
    date: str
    comment: str
    language: str
    target_topics: List[str]


class TurtleStoryChain:
    def __init__(self, config: AppConfig, llm_client: LLMClient):
        self.config = config
        self.llm_client = llm_client

    def run(self, variables: TurtleStoryChainVariables) -> str:
        instructions = TURTLE_STORY_PROMPT_TEMPLATE.to_string(
            language=self.config.GENERATION_LANGUAGE, 
            current_date=variables['date']
        )
        
        historical_event = variables['target_topics'][0]
        
        messages = [
            {"role": "system", "content": instructions},
            {
                "role": "user", 
                "content": f"Write a story about this historical event: {historical_event}"
            }
        ]
        
        resp = self.llm_client.create_completion(
            messages=messages,
            max_tokens=1024,
        )
        
        return resp.content

    def enrich_run_variables(
        self,
        date: str,
        target_topics: List[str],
    ) -> TurtleStoryChainVariables:
        return TurtleStoryChainVariables(
            target_topics=target_topics,
            date=f"{date} ({get_day_of_week(date)})",
            language=self.config.GENERATION_LANGUAGE,
            comment="",
        )