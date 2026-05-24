# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the generator

```bash
# Standard run — prompts for any .env values that are empty
python3 src/thumbnail.py

# Override any value at the command line
python3 src/thumbnail.py --title "My Video" --vibe "dark tech"

# Generate and push to GitHub in one command
python3 src/thumbnail.py --push
```

Via the Claude Code skill (recommended):
```
/thumbnail
```

Via Jupyter:
```bash
jupyter notebook notebooks/thumbnail.ipynb
```

## GitHub management

```bash
python3 src/github_manager.py           # init local repo, create GitHub repo, push
python3 src/github_manager.py --push    # push updates (repo already exists)
python3 src/github_manager.py --status  # show git status and remotes
```

## Install dependencies

```bash
pip install -r requirements.txt
```

## Architecture

The pipeline is linear: `thumbnail.py` (CLI orchestrator) calls the three worker modules in sequence, then saves the result.

```
/thumbnail (Claude Code skill)
        │
        ▼
src/thumbnail.py          ← reads .env, parses CLI args, interactive prompts for blanks
    │           │           │
    ▼           ▼           ▼
claude_helper  image_      compositor.py
.py            generator.py
    │               │           │
Claude API      gpt-image-1  Pillow
(prompt +       (1536×1024   (center-crop to target dims,
 palette)        b64_json)    title/subtitle overlays, footer)
```

- **`claude_helper.py`** — two separate Claude calls, both with `cache_control: ephemeral` on their system prompts. `generate_dalle_prompt()` returns a DALL-E scene description; `generate_palette()` returns a 6-key JSON color dict. Prompt caching cuts Claude cost ~90% on repeated vibes.
- **`image_generator.py`** — calls OpenAI `gpt-image-1` at `1536×1024` (closest 16:9), returns a PIL Image decoded from base64.
- **`compositor.py`** — center-crops the AI image to the target dimensions, composites a semi-transparent overlay (skipped when `overlay` is `#000000`), draws title/subtitle with drop shadows, and pastes a semi-transparent footer bar with company info.

## Configuration

All config lives in `.env` (gitignored). Copy `.env.example` to get started. Key variables:

| Variable | Notes |
|---|---|
| `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` | Required API keys |
| `DEFAULT_VIBE` | Natural language style — drives both the DALL-E prompt and the color palette |
| `TITLE` / `SUBTITLE` | Leave empty in `.env` to be prompted interactively each run |
| `CLAUDE_MODEL` | Defaults to `claude-sonnet-4-6` |
| `IMAGE_WIDTH` / `IMAGE_HEIGHT` | Output dimensions, default `1280×720` |
| `GITHUB_TOKEN` / `GITHUB_USERNAME` / `GITHUB_REPO` / `GITHUB_BRANCH` | Used by `github_manager.py` and `--push` flag |

## Vibe string

`DEFAULT_VIBE` is free-form natural language fed directly to Claude. Claude's palette system prompt has explicit rules for keywords like `teal`, `dark teal`, `black`, and `no overlay` — use these for predictable color output.

## Output

Thumbnails are saved to `output/thumbnail_YYYYMMDD_HHMMSS.png` (gitignored). The `output/` and `assets/` directories are kept in git via `.gitkeep` files.
