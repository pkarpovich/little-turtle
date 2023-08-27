IMAGE_PROMPTS_GENERATOR_PROMPT = """\
Based on the story, you should generate an image prompt for the image generation tool.
 
The target image should look like a children's book illustration in Pixar style. 
Your prompt must be extremely detailed, specific, and imaginative, in order to generate the most unique and creative images possible.
This prompt must be imaginative and descriptive, extrapolating information from the story input provided, such as subjects, image medium, composition, environment, lighting, colors, mood and tone, and likeness
Avoid unuseful formulations, since the noun keywords are the most important, so try to limit yourself to the most important concepts.
Include details like angle, materials, and technique to get a more accurate and desirable result
In every story, there should be a little turtle in the hat.
Image prompt should not end with point.

Story example 1:
{story_example_1}

Prompt example 1:
{prompt_example_1}

Story example 2:
{story_example_2}

Prompt example 2:
{prompt_example_2}


New story:
{new_story}

Prompt is:
"""
