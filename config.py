"""Vibe Diary Configuration"""
import os
from pathlib import Path

# Paths
CLAUDE_DIR = Path.home() / ".claude"
VIBE_DIARY_DIR = CLAUDE_DIR / "vibe-diary"
SESSIONS_DIR = VIBE_DIARY_DIR / "sessions"
POSTS_DIR = VIBE_DIARY_DIR / "posts"

# API Keys (for summarization)
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# Tools to log (skip Read - too verbose)
LOGGED_TOOLS = {"Write", "Edit", "Bash", "Grep", "Glob", "WebSearch", "WebFetch", "Task"}

# Ensure directories exist
SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
POSTS_DIR.mkdir(parents=True, exist_ok=True)
