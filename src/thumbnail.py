"""
thumbnail.py — CLI entry point for the thumbnail generator.

All configuration is loaded from .env. Any required value that is empty
will be queried interactively at runtime.

Usage:
  python3 src/thumbnail.py
  python3 src/thumbnail.py --title "My Title" --vibe "dark tech"
  python3 src/thumbnail.py --push    # generate + push output to GitHub
"""

import argparse
import os
import sys
import time
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

import claude_helper
import compositor
import image_generator
import github_manager


def parse_args() -> argparse.Namespace:
    """CLI args fall back to .env values; .env values fall back to sensible defaults."""
    parser = argparse.ArgumentParser(description="Generate a YouTube thumbnail")
    parser.add_argument("--title",         default=os.getenv("TITLE", ""))
    parser.add_argument("--subtitle",      default=os.getenv("SUBTITLE", ""))
    parser.add_argument("--vibe",          default=os.getenv("DEFAULT_VIBE", "bold energetic"))
    parser.add_argument("--company-name",  default=os.getenv("COMPANY_NAME", ""))
    parser.add_argument("--company-url",   default=os.getenv("COMPANY_URL", ""))
    parser.add_argument("--company-email", default=os.getenv("COMPANY_EMAIL", ""))
    parser.add_argument("--model",         default=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"))
    parser.add_argument("--width",  type=int, default=int(os.getenv("IMAGE_WIDTH", "1280")))
    parser.add_argument("--height", type=int, default=int(os.getenv("IMAGE_HEIGHT", "720")))
    parser.add_argument("--push",   action="store_true", help="Push project to GitHub after generating")
    return parser.parse_args()


def prompt_if_empty(value: str, field_name: str) -> str:
    if not value or not value.strip():
        value = input(f"Enter {field_name}: ").strip()
    return value


def print_banner(args: argparse.Namespace):
    w = 48
    print(f"\n┌{'─'*w}┐")
    print(f"│{'THUMBNAIL GENERATOR':^{w}}│")
    print(f"├{'─'*18}┬{'─'*(w-19)}┤")
    rows = [
        ("Title",       args.title),
        ("Subtitle",    args.subtitle),
        ("Vibe",        args.vibe),
        ("Company",     args.company_name),
        ("URL",         args.company_url),
        ("Email",       args.company_email),
        ("Output size", f"{args.width} × {args.height} px"),
        ("Model",       args.model),
    ]
    for label, val in rows:
        print(f"│ {label:<16} │ {val:<{w-20}} │")
    print(f"└{'─'*18}┴{'─'*(w-19)}┘\n")


def print_summary(output_path: Path, vibe: str, palette: dict,
                  usage_prompt: dict, usage_palette: dict, elapsed: float):
    def tokens(u: dict) -> str:
        cached = u.get("cache_read_input_tokens", 0)
        return (f"in={u['input_tokens']} out={u['output_tokens']}"
                + (f" cached={cached}" if cached else ""))

    print("\n" + "═" * 52)
    print("  THUMBNAIL COMPLETE")
    print("═" * 52)
    print(f"  Output  : {output_path}")
    print(f"  Vibe    : {vibe}")
    print(f"  Palette :")
    for k, v in palette.items():
        print(f"    {k:<20} {v}")
    print(f"  Claude  : prompt={{{tokens(usage_prompt)}}}  palette={{{tokens(usage_palette)}}}")
    print(f"  DALL-E  : ~$0.04 (standard 1792×1024)")
    print(f"  Time    : {elapsed:.1f}s")
    print("═" * 52 + "\n")


def main():
    load_dotenv(ROOT / ".env")
    args = parse_args()

    args.title         = prompt_if_empty(args.title,         "title")
    args.subtitle      = prompt_if_empty(args.subtitle,      "subtitle")
    args.vibe          = prompt_if_empty(args.vibe,          "vibe (e.g. bold energetic)")
    args.company_name  = prompt_if_empty(args.company_name,  "company name")
    args.company_url   = prompt_if_empty(args.company_url,   "company URL")
    args.company_email = prompt_if_empty(args.company_email, "company email")

    print_banner(args)

    start = time.time()

    print("→ Asking Claude to write the DALL-E prompt and color palette...")
    dalle_prompt, usage_prompt = claude_helper.generate_dalle_prompt(
        args.title, args.subtitle, args.vibe, model=args.model
    )
    palette, usage_palette = claude_helper.generate_palette(args.vibe, model=args.model)

    print(f"  DALL-E prompt: {dalle_prompt[:120]}...")
    print(f"  Palette: {palette}")

    print("→ Generating image with DALL-E 3...")
    ai_image = image_generator.generate(dalle_prompt, args.width, args.height)

    print("→ Compositing title, subtitle, and footer...")
    final_image = compositor.compose(
        ai_image=ai_image,
        title=args.title,
        subtitle=args.subtitle,
        palette=palette,
        company_name=args.company_name,
        company_url=args.company_url,
        company_email=args.company_email,
        width=args.width,
        height=args.height,
    )

    output_dir = ROOT / "output"
    output_dir.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = output_dir / f"thumbnail_{timestamp}.png"
    final_image.convert("RGB").save(str(output_path), format="PNG")

    elapsed = time.time() - start
    print_summary(output_path, args.vibe, palette, usage_prompt, usage_palette, elapsed)

    if args.push:
        print("→ Pushing project to GitHub...")
        cfg = github_manager.load_config()
        github_manager.init_local_repo(cfg["branch"])
        github_manager.stage_and_commit()
        github_manager.create_github_repo(cfg)
        github_manager.set_remote(cfg)
        github_manager.push(cfg)


if __name__ == "__main__":
    main()
