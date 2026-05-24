"""
Pillow compositor — crops AI art to target size, overlays title/subtitle, adds company footer.
"""

import os
from PIL import Image, ImageDraw, ImageFont

FOOTER_HEIGHT = 80
OVERLAY_ALPHA = 0    # no overlay — let the AI image show through clean
FOOTER_ALPHA = 230


def _hex_to_rgba(hex_color: str, alpha: int = 255) -> tuple:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (r, g, b, alpha)


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/Arial.ttf",
        "/Library/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def _center_crop(image: Image.Image, target_w: int, target_h: int) -> Image.Image:
    src_w, src_h = image.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w = int(src_w * scale)
    new_h = int(src_h * scale)
    resized = image.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return resized.crop((left, top, left + target_w, top + target_h))


def _draw_text_centered(draw: ImageDraw.ImageDraw, text: str, font, y: int,
                         canvas_w: int, fill: tuple, shadow: bool = True):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    x = (canvas_w - text_w) // 2
    if shadow:
        draw.text((x + 2, y + 2), text, font=font, fill=(0, 0, 0, 180))
    draw.text((x, y), text, font=font, fill=fill)


def compose(
    ai_image: Image.Image,
    title: str,
    subtitle: str,
    palette: dict,
    company_name: str,
    company_url: str,
    company_email: str,
    width: int = 1280,
    height: int = 720,
) -> Image.Image:
    """
    Composite the AI-generated image with text overlays and footer.
    Returns a finished PIL Image (RGBA).
    """
    canvas = _center_crop(ai_image, width, height).convert("RGBA")

    overlay_color = _hex_to_rgba(palette.get("overlay", "#000000"), OVERLAY_ALPHA)
    overlay = Image.new("RGBA", (width, height), overlay_color)
    canvas = Image.alpha_composite(canvas, overlay)

    draw = ImageDraw.Draw(canvas)

    title_font = _load_font(104, bold=True)
    subtitle_font = _load_font(58)
    footer_font = _load_font(30)

    title_color = _hex_to_rgba(palette.get("title_text", "#FFFFFF"))
    subtitle_color = _hex_to_rgba(palette.get("subtitle_text", "#EEEEEE"))

    title_y = int(height * 0.18)
    _draw_text_centered(draw, title, title_font, title_y, width, title_color, shadow=True)

    subtitle_y = title_y + 110
    _draw_text_centered(draw, subtitle, subtitle_font, subtitle_y, width, subtitle_color, shadow=True)

    footer_bg_color = _hex_to_rgba(palette.get("footer_bg", "#1A1A1A"), FOOTER_ALPHA)
    footer_layer = Image.new("RGBA", (width, FOOTER_HEIGHT), footer_bg_color)
    canvas.paste(footer_layer, (0, height - FOOTER_HEIGHT), footer_layer)

    draw = ImageDraw.Draw(canvas)
    footer_text_color = _hex_to_rgba(palette.get("footer_text", "#FFFFFF"))
    footer_line = f"{company_name}  ·  {company_url}  ·  {company_email}"
    footer_y = height - FOOTER_HEIGHT + (FOOTER_HEIGHT - 30) // 2
    _draw_text_centered(draw, footer_line, footer_font, footer_y, width, footer_text_color, shadow=False)

    return canvas
