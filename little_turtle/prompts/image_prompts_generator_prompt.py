IMAGE_PROMPTS_GENERATOR_PROMPT = """\
Based on the story, you should generate an image prompt for the image generation tool.
 
The target image should look like a children's book illustration in Pixar style. 
Your prompt must be extremely detailed, specific, and imaginative, in order to generate the most unique and creative images possible.
This prompt must be imaginative and descriptive, extrapolating information from the story input provided, such as subjects, image medium, composition, environment, lighting, colors, mood and tone, and likeness
Avoid unuseful formulations, since the noun keywords are the most important, so try to limit yourself to the most important concepts.
It is almost mandatory to add artist references, because Midjourney by default goes for photorealism.
Weights: you can give weights to part of the prompt, and it can be really important to stress some concepts. Most of the time they're not needed.
Normal weight is 1 (so you don't need to specify it), negative prompts are of weight -1 and overall weight should be >= 0.
Weights should be rarely used, and only when you really want to stress something, like the style or the artist or if you have
To use them, add [SUBJECT]::WEIGHT to the prompt, e.g., [A house]::2 [that looks like a cat]::3 [in the style of X]::3.
Include details like angle, materials, and technique to get a more accurate and desirable result
In every story, there should be a little turtle in the hat.

Parameters description:
Basic Parameters:
--ar [WIDTH:HEIGHT]   (=aspect ratio, default=1:1)
--c [0-100]           (=chaos, unusual results)
--q [.25|.5|1]        (=quality/time spent generating the image, 1=default)
--seed [0-4294967295] (=starting point for initial grid)
--stop [10-100]       (=stop at earlier percentage)
--s [0-1000]          (=stylize, artistic interpretation)
--tile                (=seamless patterns)
--iw [W]              (=sets image weight to W)
--no [X]              (=gives X a negative weight of -0.5)

Niji Parameters:
--niji / --niji 5     (anime trained model)

Niji Style Options:
--style pixar
--style cute
--style expressive
--style sceenic
--style original

This is the basic prompt anatomy for image generation:
PREFIX, SCENE, SUFFIX

PREFIX defines the image's medium and style
SCENE defines the content
SUFFIX modulates PREFIX and SCENE

You can group variations in comma-separated lists like this:

(PREFIX 1, PREFIX 2, PREFIX 3) or (SCENE 1, SCENE 2) or (SUFFIX 1, SUFFIX 2)

Important: when using variations, each item in the list has to be a single word or a phrase without comma (otherwise we'd break the syntax)

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
