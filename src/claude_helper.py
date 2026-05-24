"""
Claude API helper — generates DALL-E prompt and color palette for a thumbnail.
Uses prompt caching on system prompts to reduce cost on repeated calls.
"""

import json
import os
import anthropic

_client: anthropic.Anthropic | None = None

SYSTEM_PROMPT_ARTIST = """You are an expert YouTube thumbnail art director with deep knowledge of visual design,
color psychology, and what makes thumbnails get clicks. You understand composition, contrast,
and how to convey energy and emotion through visual elements.

When given a title, subtitle, and vibe, you produce a detailed, vivid prompt for DALL-E 3
that describes a scene featuring a friendly robot character as the hero, a background that
matches the vibe, and a composition that leaves clear space at the top and bottom for
text overlays. Always describe the robot as expressive, dynamic, and visually interesting.
The image must be safe for all audiences and suitable for a professional YouTube channel.

Respond with ONLY the image generation prompt — no explanation, no labels, just the prompt text."""

SYSTEM_PROMPT_PALETTE = """You are a professional graphic designer specializing in color theory for digital media.
Given a vibe description, you select a harmonious color palette for a YouTube thumbnail.

Respond with ONLY a valid JSON object — no explanation, no markdown code fences — in exactly this shape:
{
  "background": "#xxxxxx",
  "title_text": "#xxxxxx",
  "subtitle_text": "#xxxxxx",
  "footer_bg": "#xxxxxx",
  "footer_text": "#xxxxxx",
  "overlay": "#xxxxxx"
}

Rules:
- When the vibe mentions "teal" or "dark teal", use dark teal (#006D6D or similar) as the dominant hue.
- When the vibe mentions "black", use near-black (#0A0A0A or #0D1117) for footer_bg and overlay.
- footer_text should be a bright teal (e.g. #00E5CC or #2AFFD8) for strong contrast on dark footer.
- title_text should be white or near-white (#FFFFFF or #F0FFFE) for maximum legibility.
- subtitle_text should be a lighter teal or white.
- overlay should be "#000000" when the vibe says "no overlay" — the compositor will skip it.
- Always ensure WCAG AA contrast between text and its background."""


def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY not set in environment")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


def generate_dalle_prompt(title: str, subtitle: str, vibe: str, model: str = "claude-sonnet-4-6") -> tuple[str, dict]:
    """
    Ask Claude to write a DALL-E 3 prompt for a thumbnail scene.
    Returns (dalle_prompt, usage_dict).
    """
    client = _get_client()
    response = client.messages.create(
        model=model,
        max_tokens=512,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT_ARTIST,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Create a DALL-E 3 image generation prompt for a YouTube thumbnail.\n\n"
                    f"Title: {title}\n"
                    f"Subtitle: {subtitle}\n"
                    f"Vibe: {vibe}\n\n"
                    f"The image must be 16:9 landscape orientation (1792x1024 will be generated).\n"
                    f"Feature a friendly expressive robot as the main character.\n"
                    f"Leave the top 25% and bottom 15% relatively uncluttered for text overlays.\n"
                    f"Make it visually stunning and click-worthy."
                ),
            }
        ],
    )
    prompt_text = response.content[0].text.strip()
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
        "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
    }
    return prompt_text, usage


def generate_palette(vibe: str, model: str = "claude-sonnet-4-6") -> tuple[dict, dict]:
    """
    Ask Claude for a color palette dict matching the given vibe.
    Returns (palette_dict, usage_dict).
    """
    client = _get_client()
    response = client.messages.create(
        model=model,
        max_tokens=256,
        system=[
            {
                "type": "text",
                "text": SYSTEM_PROMPT_PALETTE,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"Vibe: {vibe}",
            }
        ],
    )
    raw = response.content[0].text.strip()
    palette = json.loads(raw)
    usage = {
        "input_tokens": response.usage.input_tokens,
        "output_tokens": response.usage.output_tokens,
        "cache_creation_input_tokens": getattr(response.usage, "cache_creation_input_tokens", 0),
        "cache_read_input_tokens": getattr(response.usage, "cache_read_input_tokens", 0),
    }
    return palette, usage
