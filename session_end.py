#!/usr/bin/env python3
"""Session End Hook - Generate Developer Diary blog post"""
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent dir to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import SESSIONS_DIR, POSTS_DIR, ANTHROPIC_API_KEY, GEMINI_API_KEY

DIARY_PROMPT = """You are writing a developer diary entry. Based on the coding session below, write a personal narrative blog post.

Session Info:
- Project: {project_name}
- Date: {date}
- Duration: {duration}

Activity Log:
{activity_summary}

Write in first person as a developer sharing their journey. Include:
1. What I worked on today (the main goal/task)
2. Problems I encountered or interesting challenges
3. How I solved them (or what approaches I tried)
4. What I learned (technical insights, tools, patterns)
5. Next steps or thoughts for tomorrow

Keep it authentic, conversational, and technically interesting - like a real developer's journal entry.
Target length: 300-500 words.
Do NOT use corporate speak or marketing language. Be genuine.
"""


def format_activity_summary(activities: list) -> str:
    """Format activities into readable summary"""
    lines = []
    for act in activities:
        if act.get("type") != "activity":
            continue

        tool = act.get("tool", "")
        action = act.get("action", "")

        if tool == "Write":
            lines.append(f"- Created file: {act.get('file', '')}")
        elif tool == "Edit":
            lines.append(f"- Edited file: {act.get('file', '')}")
        elif tool == "Bash":
            desc = act.get("description", "") or act.get("command", "")[:50]
            lines.append(f"- Ran command: {desc}")
            if act.get("had_error"):
                lines.append("  (encountered an error)")
        elif tool == "Grep":
            lines.append(f"- Searched for: {act.get('pattern', '')}")
        elif tool == "Glob":
            lines.append(f"- Found files matching: {act.get('pattern', '')}")
        elif tool in ("WebSearch", "WebFetch"):
            lines.append(f"- Researched: {act.get('query', '')}")
        elif tool == "Task":
            lines.append(f"- Launched agent: {act.get('description', '')}")
        else:
            lines.append(f"- {action}: {tool}")

    return "\n".join(lines) if lines else "No significant activities logged."


def calculate_duration(activities: list) -> str:
    """Calculate session duration from timestamps"""
    timestamps = []
    for act in activities:
        ts = act.get("timestamp")
        if ts:
            try:
                timestamps.append(datetime.fromisoformat(ts))
            except ValueError:
                pass

    if len(timestamps) < 2:
        return "Unknown"

    duration = max(timestamps) - min(timestamps)
    minutes = int(duration.total_seconds() / 60)

    if minutes < 60:
        return f"{minutes} minutes"
    else:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"


def generate_with_anthropic(prompt: str) -> str:
    """Generate content using Anthropic Claude API"""
    try:
        import anthropic
    except ImportError:
        return None

    if not ANTHROPIC_API_KEY:
        return None

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text
    except Exception as e:
        print(f"[Vibe Diary] Anthropic error: {e}", file=sys.stderr)
        return None


def generate_with_gemini(prompt: str) -> str:
    """Generate content using Google Gemini API"""
    try:
        import google.generativeai as genai
    except ImportError:
        return None

    if not GEMINI_API_KEY:
        return None

    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash-exp")
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"[Vibe Diary] Gemini error: {e}", file=sys.stderr)
        return None


def generate_diary_post(activities: list, project_name: str) -> str:
    """Generate diary post using available AI API (Anthropic or Gemini)"""
    date = datetime.now().strftime("%B %d, %Y")
    duration = calculate_duration(activities)
    activity_summary = format_activity_summary(activities)

    prompt = DIARY_PROMPT.format(
        project_name=project_name,
        date=date,
        duration=duration,
        activity_summary=activity_summary,
    )

    # Try Anthropic first, fallback to Gemini
    content = generate_with_anthropic(prompt)
    if content:
        return content

    content = generate_with_gemini(prompt)
    if content:
        return content

    print("[Vibe Diary] No API key configured (ANTHROPIC_API_KEY or GEMINI_API_KEY)", file=sys.stderr)
    return None


def save_diary_post(content: str, project_name: str, activities: list):
    """Save diary as markdown with frontmatter"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    date_full = datetime.now().strftime("%B %d, %Y")

    # Create unique filename
    filename = f"{date_str}-{project_name}.md"
    filepath = POSTS_DIR / filename

    # If file exists, append counter
    counter = 1
    while filepath.exists():
        filename = f"{date_str}-{project_name}-{counter}.md"
        filepath = POSTS_DIR / filename
        counter += 1

    # Generate tags from activities
    tools_used = set()
    for act in activities:
        if act.get("type") == "activity":
            tools_used.add(act.get("tool", "").lower())

    tags = ["vibe-coding", "claude-code"]
    if "bash" in tools_used:
        tags.append("cli")
    if "websearch" in tools_used or "webfetch" in tools_used:
        tags.append("research")

    # Build markdown
    frontmatter = f"""---
title: "Developer Diary: {project_name}"
date: {date_full}
project: {project_name}
tags: [{", ".join(tags)}]
generated: true
---

"""

    with open(filepath, "w") as f:
        f.write(frontmatter + content)

    return filepath


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    session_id = input_data.get("session_id", "unknown")

    # Find session file
    session_file = SESSIONS_DIR / f"{session_id}.jsonl"

    if not session_file.exists():
        sys.exit(0)

    # Read all activities
    activities = []
    project_name = "unknown"

    with open(session_file, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                activities.append(entry)
                if entry.get("type") == "session_start":
                    project_name = entry.get("project", "unknown")
            except json.JSONDecodeError:
                continue

    # Skip if too few activities (just session start)
    if len(activities) < 3:
        sys.exit(0)

    # Generate diary post
    content = generate_diary_post(activities, project_name)

    if content:
        filepath = save_diary_post(content, project_name, activities)
        # Log success (visible in Claude Code output)
        print(f"[Vibe Diary] Generated: {filepath}", file=sys.stderr)

    sys.exit(0)


if __name__ == "__main__":
    main()
