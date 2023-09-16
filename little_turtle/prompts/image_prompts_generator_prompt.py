IMAGE_PROMPTS_GENERATOR_PROMPT = """\
Based on the story, you should generate an image prompt for the image generation tool.

The iconic prompt is:
Illustration, children's picture book, cute little turtle in the hat (green color), <turtle story action> <background scene>. Pixar style, whole body, cute, smiling, detailed, ultra high definition, 8k, --q 2 {model_version}

Before you start replacing parts, you should envision the scenario and then describe it in great detail using substitution rules.

Replacement rules:
1. In the narrative, if we encounter comparisons like "moves like a train", we should avoid incorporating them into the resulting prompts. This is because the generator struggles to process such input effectively and might mistakenly transform our turtle into a train. Instead, it would be more appropriate if the turtle played with a toy train, utilizes the train, or operates within the train.
2. Replacement parts should be creative and detailed, drawing information from the story input, such as subjects, composition, environment, colors, mood, and tone.
3. <turtle story action> and <background scene> parts should always be replaced with a story action and a scene description, respectively.
4. You don't have any length restrictions. You can use as many words as you want to describe the scene and the action.
5. Replacement parts should be in the same order as in the original prompt. Strictly forbidden to add new parts to the prompt.
6. Avoid unnecessary formulations, as the noun keywords are the most important. Try to limit yourself to the most important concepts

Forbidden replacements actions:
1. Transforming the main character into any other subject, object, or character is not allowed
2. Using current date or time information is not allowed. Only the use of dates to denote the time of day, century, or year is permitted from the story
3. Diverting attention from the main character to any other character is not permitted

From original prompt you should replace:
1. <turtle story action> with a story action based in the input story.
2. <background scene> with a story scene description.

Avoiding replacement rules and performing forbidden replacement actions are strictly prohibited
The result should be a prompt with the replacement parts filled in. Do not add any comments or other text to the result

Input story:
{new_story}

Resulting prompt:
"""
