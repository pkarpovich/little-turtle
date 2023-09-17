STORY_SUMMARIZATION_PROMPT_TEMPLATE = """\
Based on the input story, extract the day's event.
The result should be a single sentence with a brief event description.
Refrain from using today's date in the result.
Keep original event date and time in the result.
The result should be in {language}.
If you cannot extract an event, simply return an empty string.

Story is:
{story}

Result event is:
"""
