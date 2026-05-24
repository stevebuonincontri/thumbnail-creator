# /thumbnail — AI Thumbnail Generator

Generate a 1280×720 YouTube thumbnail using Claude + OpenAI, then optionally push to GitHub.

## Steps

1. **Read configuration from `.env`**
   All settings — API keys, company info, vibe, title, subtitle, model, and GitHub credentials — live in `.env`.
   Copy `.env.example` to `.env` and fill in your values if `.env` doesn't exist.

2. **Resolve required inputs** — use `.env` values if non-empty; otherwise ask the user:
   - `TITLE` — main heading on the thumbnail
   - `SUBTITLE` — secondary line below the title
   - `DEFAULT_VIBE` — mood/style (e.g. "bold dark teal black no overlay"); ask if missing
   - `COMPANY_NAME`, `COMPANY_URL`, `COMPANY_EMAIL` — ask for any that are empty

3. **Print pre-run summary** in a formatted table:
   ```
   ┌────────────────────────────────────────────────┐
   │                THUMBNAIL GENERATOR             │
   ├──────────────────┬─────────────────────────────┤
   │ Title            │ <TITLE>                     │
   │ Subtitle         │ <SUBTITLE>                  │
   │ Vibe             │ <DEFAULT_VIBE>              │
   │ Company          │ <COMPANY_NAME>              │
   │ URL              │ <COMPANY_URL>               │
   │ Email            │ <COMPANY_EMAIL>             │
   │ Output size      │ 1280 × 720 px               │
   │ Model            │ <CLAUDE_MODEL>              │
   └──────────────────┴─────────────────────────────┘
   ```

4. **Run the generator**
   ```bash
   python3 src/thumbnail.py
   ```
   Optional flags:
   ```bash
   python3 src/thumbnail.py --title "Override Title" --vibe "dark tech"
   python3 src/thumbnail.py --push    # generate + commit + push to GitHub
   ```

5. **Print post-run summary** showing:
   - Output file path
   - Vibe and color palette used
   - Claude token usage (input / output / cache hits)
   - OpenAI image cost estimate
   - Total elapsed time

6. **GitHub sync (optional)**
   To push the project to GitHub separately:
   ```bash
   python3 src/github_manager.py          # init + create repo + push
   python3 src/github_manager.py --push   # push only (repo already exists)
   python3 src/github_manager.py --status # show git status
   ```
   Reads `GITHUB_TOKEN`, `GITHUB_USERNAME`, `GITHUB_REPO`, `GITHUB_BRANCH` from `.env`.

## Notes
- Output images are saved to `output/thumbnail_YYYYMMDD_HHMMSS.png` (gitignored)
- All configuration is in `.env` — never commit this file (it's in `.gitignore`)
- Use `.env.example` as the safe, committable template
- TITLE and SUBTITLE can be left empty in `.env` to be prompted each run
- GitHub repo: https://github.com/stevebuonincontri/thumbnail-creator
