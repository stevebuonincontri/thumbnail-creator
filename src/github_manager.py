"""
GitHub manager — initializes the local git repo, creates the remote repo via
the GitHub API, and pushes. All credentials are read from .env.

Usage:
  python3 src/github_manager.py           # init + create repo + push
  python3 src/github_manager.py --push    # push only (repo already exists)
  python3 src/github_manager.py --status  # show local git status
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).parent.parent


def _run(cmd: list[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    kwargs = {"cwd": str(ROOT), "check": check}
    if capture:
        kwargs["capture_output"] = True
        kwargs["text"] = True
    return subprocess.run(cmd, **kwargs)


def _git(*args, check: bool = True, capture: bool = False):
    return _run(["git"] + list(args), check=check, capture=capture)


def load_config() -> dict:
    load_dotenv(ROOT / ".env")
    token    = os.environ.get("GITHUB_TOKEN", "").strip()
    username = os.environ.get("GITHUB_USERNAME", "").strip()
    repo     = os.environ.get("GITHUB_REPO", "thumbnail-creator").strip()
    branch   = os.environ.get("GITHUB_BRANCH", "main").strip()

    missing = [k for k, v in [("GITHUB_TOKEN", token), ("GITHUB_USERNAME", username)] if not v]
    if missing:
        print(f"✗ Missing in .env: {', '.join(missing)}")
        print("  Add them and re-run.")
        sys.exit(1)

    return {"token": token, "username": username, "repo": repo, "branch": branch}


def is_git_repo() -> bool:
    result = _run(["git", "rev-parse", "--git-dir"], check=False, capture=True)
    return result.returncode == 0


def init_local_repo(branch: str):
    if is_git_repo():
        print("✓ Git repo already initialized")
        return
    print("→ Initializing local git repo...")
    _git("init", "-b", branch)
    _git("config", "user.name", "Steve Buonincontri")
    _git("config", "user.email", "stevebuonincontri@gmail.com")
    print("✓ Local repo initialized")


def stage_and_commit():
    result = _git("status", "--porcelain", capture=True)
    if not result.stdout.strip():
        print("✓ Nothing to commit — working tree clean")
        return
    print("→ Staging files...")
    _git("add", ".")
    result = _git("log", "--oneline", "-1", check=False, capture=True)
    if result.returncode != 0:
        msg = "Initial commit — thumbnail-creator project"
    else:
        msg = "Update project files"
    _git("commit", "-m", msg)
    print(f"✓ Committed: {msg}")


def repo_exists_on_github(cfg: dict) -> bool:
    url = f"https://api.github.com/repos/{cfg['username']}/{cfg['repo']}"
    resp = requests.get(url, headers={"Authorization": f"token {cfg['token']}"})
    return resp.status_code == 200


def create_github_repo(cfg: dict):
    if repo_exists_on_github(cfg):
        print(f"✓ Remote repo already exists: github.com/{cfg['username']}/{cfg['repo']}")
        return

    print(f"→ Creating GitHub repo: {cfg['username']}/{cfg['repo']}...")
    url = "https://api.github.com/user/repos"
    payload = {
        "name": cfg["repo"],
        "description": "AI-powered YouTube thumbnail generator using Claude + OpenAI",
        "private": False,
        "auto_init": False,
    }
    resp = requests.post(
        url,
        json=payload,
        headers={
            "Authorization": f"token {cfg['token']}",
            "Accept": "application/vnd.github+json",
        },
    )
    if resp.status_code == 201:
        print(f"✓ Repo created: {resp.json()['html_url']}")
    else:
        print(f"✗ Failed to create repo: {resp.status_code} — {resp.json().get('message')}")
        sys.exit(1)


def set_remote(cfg: dict):
    remote_url = f"https://{cfg['token']}@github.com/{cfg['username']}/{cfg['repo']}.git"
    result = _git("remote", "get-url", "origin", check=False, capture=True)
    if result.returncode == 0:
        _git("remote", "set-url", "origin", remote_url)
    else:
        _git("remote", "add", "origin", remote_url)
    print("✓ Remote 'origin' configured")


def push(cfg: dict):
    print(f"→ Pushing to github.com/{cfg['username']}/{cfg['repo']} ({cfg['branch']})...")
    _git("push", "-u", "origin", cfg["branch"])
    print(f"✓ Pushed — https://github.com/{cfg['username']}/{cfg['repo']}")


def print_status():
    if not is_git_repo():
        print("Not a git repository. Run without --status to initialize.")
        return
    _git("status")
    result = _git("remote", "-v", check=False, capture=True)
    if result.stdout.strip():
        print("\nRemotes:")
        print(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="Manage GitHub repo for this project")
    parser.add_argument("--push",   action="store_true", help="Push only (skip repo creation)")
    parser.add_argument("--status", action="store_true", help="Show git status and remotes")
    args = parser.parse_args()

    if args.status:
        print_status()
        return

    cfg = load_config()

    init_local_repo(cfg["branch"])
    stage_and_commit()

    if not args.push:
        create_github_repo(cfg)

    set_remote(cfg)
    push(cfg)

    print("\n" + "═" * 52)
    print("  GITHUB SYNC COMPLETE")
    print("═" * 52)
    print(f"  Repo  : https://github.com/{cfg['username']}/{cfg['repo']}")
    print(f"  Branch: {cfg['branch']}")
    print("═" * 52 + "\n")


if __name__ == "__main__":
    main()
