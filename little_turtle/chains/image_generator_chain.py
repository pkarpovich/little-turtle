from openai import OpenAI


class ImageGeneratorChain:
    model_name: str = "dall-e-3"

    def __init__(self):
        self.client = OpenAI()

    def run(self, story_prompt: str) -> str:
        response = self.client.images.generate(
            model=self.model_name,
            prompt=story_prompt,
            size="1024x1024",
            quality="hd",
            n=1,
        )

        return response.data[0].url