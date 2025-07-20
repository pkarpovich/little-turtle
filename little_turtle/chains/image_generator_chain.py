from prompt_template import PromptTemplate

from little_turtle.services import AppConfig
from little_turtle.llm_provider import LLMClient


template = PromptTemplate("""Draw a square, Pixar-style digital illustration inspired by this historical story.

The main character is an anthropomorphic teenage turtle: extremely cute, with a round face, big sparkling eyes, a gentle smile, soft green skin, and always wearing a cozy brown knit beanie (signature hat) and a scarf. **The turtle should be proportionally sized - about 3-4 feet tall when standing upright, similar to a young teenager compared to adult humans or appropriately scaled to surrounding objects.**

**The historical event itself should be the visual focus of the composition, taking center stage in the frame. The turtle should be positioned as an observer or participant in the background or to the side**, naturally blending into the scene, never overshadowing the key event, but reacting with curiosity, joy, or awe.

Capture the accurate setting, era, clothing, technology, and unique mood of the described event. **Ensure the main historical action, key figures, or significant moments dominate the visual hierarchy.**

Use vibrant colors, soft Pixar lighting, and expressive, cinematic details. **Apply dramatic lighting and composition techniques to highlight the historical event while the turtle adds charm without stealing focus.**

The scene should be lively and dynamic, with the turtle's pose, gaze, and body language fitting the context and spirit of the story.
Do not add story date or year inside image. Aspect ratio: 1:1 (square).""")


class ImageGeneratorChain:
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client

    def run(self, story: str) -> str:
        instructions = template.to_string()
        return self.llm_client.generate_image(instructions, story)