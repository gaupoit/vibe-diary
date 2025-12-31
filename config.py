"""Vibe Diary Configuration"""
import os
from pathlib import Path

# Paths
CLAUDE_DIR = Path.home() / ".claude"
VIBE_DIARY_DIR = CLAUDE_DIR / "vibe-diary"

# Load .env file if exists (for hook subprocess env vars)
_env_file = VIBE_DIARY_DIR / ".env"
if _env_file.exists():
    with open(_env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())
SESSIONS_DIR = VIBE_DIARY_DIR / "sessions"
POSTS_DIR = VIBE_DIARY_DIR / "posts"

# API Keys (for summarization)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# WordPress Configuration
WORDPRESS_API_URL = os.environ.get("WORDPRESS_API_URL", "https://wp.devbanhmi.com")
WORDPRESS_USER = os.environ.get("WORDPRESS_USER", "devbanhmi")
WORDPRESS_APP_PASSWORD = os.environ.get("WORDPRESS_APP_PASSWORD", "")
WORDPRESS_CATEGORY_ID = int(os.environ.get("WORDPRESS_CATEGORY_ID", "2"))  # 2 = Lessons Learned

# Tools to log (skip Read - too verbose)
LOGGED_TOOLS = {"Write", "Edit", "Bash", "Grep", "Glob", "WebSearch", "WebFetch", "Task"}

# Ensure directories exist
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
POSTS_DIR.mkdir(parents=True, exist_ok=True)
