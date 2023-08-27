from little_turtle.stores import Story


def story_response(story: Story):
    return f"""\
Story:

{story["content"]}

Image prompt:

{story["image_prompt"]}
"""


def remove_optional_last_period(text: str) -> str:
    if text[-1] == '.':
        return text[:-1]
    
    return text
