from openai import OpenAI
from prompt_template import PromptTemplate


template = PromptTemplate("""Draw a square, Pixar-style digital illustration inspired by this historical story.

The main character is an anthropomorphic teenage turtle: extremely cute, with a round face, big sparkling eyes, a gentle smile, soft green skin, and always wearing a cozy brown knit beanie (signature hat) and a scarf.

The turtle naturally blends into the historical scene, never overshadowing the key event, but reacting with curiosity, joy, or awe.

Capture the accurate setting, era, clothing, technology, and unique mood of the described event.

Use vibrant colors, soft Pixar lighting, and expressive, cinematic details.

The scene should be lively and dynamic, with the turtle’s pose, gaze, and body language fitting the context and spirit of the story.
Do not add story date inside image. Aspect ratio: 1:1 (square).""")


class ImageGeneratorChain:
    def __init__(self):
        self.client = OpenAI()

    def run(self, story: str) -> str:
        prompt = template.to_string()

        resp = self.client.responses.create(
            model='gpt-4.1',
            instructions=prompt,
            input=story,
            tools=[{"type": "image_generation"}],
        )

        image_data = [
            output.result
            for output in resp.output
            if output.type == "image_generation_call"
        ]

        return image_data[0]
