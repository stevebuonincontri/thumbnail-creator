"""
OpenAI image generator — uses gpt-image-1, returns a PIL Image.
"""

import base64
import io
import os
from PIL import Image
import openai


_client: openai.OpenAI | None = None


def _get_client() -> openai.OpenAI:
    global _client
    if _client is None:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise EnvironmentError("OPENAI_API_KEY not set in environment")
        _client = openai.OpenAI(api_key=api_key)
    return _client


def generate(prompt: str, width: int = 1280, height: int = 720) -> Image.Image:
    """
    Generate an image with gpt-image-1 using the given prompt.
    Uses 1536x1024 (closest 16:9); compositor will crop to exact target dims.
    Returns a PIL Image.
    """
    client = _get_client()

    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1536x1024",
        quality="medium",
        n=1,
    )

    image_data = response.data[0].b64_json
    image_bytes = base64.b64decode(image_data)
    image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    return image
