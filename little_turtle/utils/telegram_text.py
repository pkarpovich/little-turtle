from little_turtle.stores import Story


def story_response(story: Story):
    return f"""\
Story:

{story["content"]}

Image prompt:

{story["image_prompt"]}
"""
