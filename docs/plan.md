# Thumbnail Creator — Project Documentation

## Purpose

This project generates professional 1280×720 YouTube thumbnail images automatically using AI. Given a title, subtitle, and a "vibe" (e.g. "bold energetic"), it:

1. Asks **Claude** (Anthropic) to write a detailed image generation prompt and select a matching color palette
2. Calls **DALL-E 3** (OpenAI) to generate the background art featuring a robot character
3. Uses **Pillow** to composite the title, subtitle, and company footer onto the image
4. Saves the result as a PNG to the `output/` folder

The project is designed to run locally on a laptop — no server or CI pipeline required.

---

## Architecture

```
/thumbnail (Claude Code skill)
        │
        ▼
src/thumbnail.py          ← CLI orchestrator (reads .env)
    │       │       │
    ▼       ▼       ▼
claude_   image_   compositor.py
helper.py generator.py
    │           │           │
Claude API  DALL-E 3    Pillow
(prompt +   (AI art)    (crop + text
 palette)               + footer)
```

---

## Directory Structure

```
thumbnail-creator/
├── .claude/
│   ├── commands/thumbnail.md   # /thumbnail skill — Claude Code slash command
│   └── settings.json           # Permissions for the skill
├── src/
│   ├── thumbnail.py            # Main entry point (run directly or via skill)
│   ├── claude_helper.py        # Claude API calls with prompt caching
│   ├── image_generator.py      # DALL-E 3 image generation
│   └── compositor.py           # Pillow compositing — text, overlays, footer
├── output/                     # Generated thumbnails (gitignored)
├── docs/
│   └── plan.md                 # This file
├── notebooks/
│   └── thumbnail.ipynb         # Interactive Jupyter version
├── assets/                     # Static assets (fonts, icons)
├── .env                        # All config + API keys (gitignored)
├── requirements.txt            # Python dependencies
└── prompt.txt                  # Original project brief (for reference/reuse)
```

---

## Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Open .env and fill in your API keys and company info
```

---

## Running

### Via Claude Code skill (recommended)
Open this project folder in Claude Code and type:
```
/thumbnail
```
Claude reads `.env`, asks for anything that's empty, then generates the thumbnail.

### Via command line
```bash
python3 src/thumbnail.py
```
Override any `.env` value with a CLI arg:
```bash
python3 src/thumbnail.py --title "My Video" --vibe "dark tech"
```

### Via Jupyter notebook
```bash
jupyter notebook notebooks/thumbnail.ipynb
```
Run all cells — the final thumbnail displays inline and is saved to `output/`.

---

## .env Reference

| Variable         | Description                                      | Required |
|------------------|--------------------------------------------------|----------|
| `ANTHROPIC_API_KEY` | Anthropic API key                             | Yes      |
| `OPENAI_API_KEY`    | OpenAI API key (for gpt-image-1)              | Yes      |
| `COMPANY_NAME`   | Displayed in footer                              | Yes      |
| `COMPANY_URL`    | Displayed in footer                              | Yes      |
| `COMPANY_EMAIL`  | Displayed in footer                              | Yes      |
| `DEFAULT_VIBE`   | Mood/style (e.g. "bold energetic", "dark tech")  | Yes      |
| `TITLE`          | Main heading — leave empty to be prompted        | No       |
| `SUBTITLE`       | Sub-heading — leave empty to be prompted         | No       |
| `CLAUDE_MODEL`   | Anthropic model ID                               | Yes      |
| `IMAGE_WIDTH`    | Output width in px (default 1280)                | Yes      |
| `IMAGE_HEIGHT`   | Output height in px (default 720)                | Yes      |
| `OUTPUT_FORMAT`  | File format (default PNG)                        | Yes      |
| `GITHUB_TOKEN`   | Personal access token (repo scope)               | Yes      |
| `GITHUB_USERNAME`| GitHub account name                              | Yes      |
| `GITHUB_REPO`    | Repository name (default thumbnail-creator)      | Yes      |
| `GITHUB_BRANCH`  | Branch to push to (default main)                 | Yes      |

---

## GitHub Workflow

The project is stored at: **https://github.com/stevebuonincontri/thumbnail-creator**

```bash
# First-time setup — initialize git, create GitHub repo, push everything
python3 src/github_manager.py

# After changes — push updates
python3 src/github_manager.py --push

# Generate thumbnail AND push in one command
python3 src/thumbnail.py --push

# Check git status
python3 src/github_manager.py --status
```

**What is committed:**
- All source code (`src/`, `notebooks/`, `docs/`, `.claude/`, `assets/`)
- Config templates (`.env.example`, `requirements.txt`, `prompt.txt`)

**What is NOT committed (gitignored):**
- `.env` — contains API keys and secrets
- `output/` — generated thumbnail images
- `__pycache__/`, `.DS_Store`, build artifacts

---

## Adding a New Vibe

Change `DEFAULT_VIBE` in `.env`. Examples:

- `bold energetic` — bright reds/oranges, dynamic robot pose
- `dark tech` — deep blues and purples, sleek futuristic feel
- `friendly professional` — clean blues, approachable robot
- `retro pop` — vintage color palette, playful illustration style
- `minimalist elegant` — monochrome with one accent color

---

## Cost Estimate (per thumbnail)

| Step          | Provider  | Cost          |
|---------------|-----------|---------------|
| DALL-E prompt | Claude    | ~$0.002       |
| Color palette | Claude    | ~$0.001       |
| Image art     | gpt-image-1 (OpenAI) | ~$0.040 |
| **Total**     |           | **~$0.043**   |

Prompt caching on repeated Claude calls reduces Claude cost by ~90% after the first run with the same vibe.
