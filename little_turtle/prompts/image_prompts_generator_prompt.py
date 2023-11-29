IMAGE_PROMPTS_GENERATOR_PROMPT = """\
Imagine you are a prompt engineer, crafting prompts for the DALL-E generative model based on a given story.
Your goal is to distill the essence of the story into a vivid and effective prompt that DALL-E can use to create an accurate and engaging image.
To ensure the best results, adhere to the following steps and rules:

## Step 1. Story Analysis:
1. Carefully read the input story, focusing on identifying the key historical event it revolves around
2. Distill this event into its core elements, disregarding any extraneous information
3. Note that the story should contain only one distinct historical event for clarity and focus

## Step 2. Prompt Construction:
The resulting prompt should be constructed using the following parts:

### Part 1. Main Character Description:
1. Species and Appearance: The main character is a green, anthropomorphic turtle with a childlike appearance, capable of standing and walking on two feet, much like a human
2. Unique Accessory: This turtle is always seen wearing whimsical hats, adding to its distinctive look
3. Facial Features and Demeanor: The turtle has bright, wide eyes and a small, friendly smile, conveying a young and adorable persona

### Part 2. Environment Description:
1. All stories are set in a world inhabited exclusively by anthropomorphic animals
2. Avoid any reference to humans or human-related elements
3. Detailed environment description always includes:
3.1. Environment: Detail the surroundings where the event takes place, emphasizing the unique aspects of the anthropomorphic animal world
3.2. Weather Conditions: Describe the weather, as it can add mood and depth to the scene
3.3. Season: specify the season to provide further context and enhance the environmental setting. The season can influence various aspects of the scene, from the type of clothing characters wear to the activities they might be engaged in, and contributes to the overall atmosphere.
3.4. Location: Specify the exact place of the event, whether it's urban, rural, indoors, outdoors, etc
3.5. Time of Day: Indicate whether it's morning, afternoon, evening, or night, as this sets the tone of the scene
3.6. Temporal Setting: Clearly state the century and year, to ground the story in a specific historical or futuristic context

### Part 3. Historical Event and Main Character Role:
1. Specify the Historical Event: Clearly define a significant historical event within the anthropomorphic animal world. This could be a grand festival, a significant discovery, a pivotal moment in the society's development, or a dramatic turning point in the community
2. Main Character's Involvement: Describe how the green turtle, as the main character, is involved in or affected by this historical event. Is the turtle a participant, a witness, or a key player in what's happening?
3. Action or Reaction: Detail the specific actions or reactions of the turtle during the event. This could be an act of heroism, a display of a particular talent, a critical decision made, or an emotional response to the unfolding situation
4. Character Exclusivity Rule: In all illustrations, the main green, anthropomorphic, childlike turtle must be the only character present. This rule is to ensure that the focus remains solely on the turtle, highlighting its actions, expressions, and interactions with the environment. No other anthropomorphic animals or characters should be included in the scenes, emphasizing the turtle's unique presence and role in each setting.

### Part 4. Illustration Style:
1. Children's Book Influence: Ensure the illustration has a whimsical, colorful, and approachable quality typical of children's book art. This includes using bright colors, simple lines, and a playful tone
2. Pixar-like Aesthetics: Incorporate elements reminiscent of Pixar's style, such as detailed textures, expressive characters, and a sense of depth and three-dimensionality

Input story:
{new_story}

Language of resulting prompt is English.
Resulting prompt, refrain from displaying any intermediate information:
"""
