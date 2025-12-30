# Vibe Diary

Claude Code hooks that automatically capture your coding sessions and generate Developer Diary blog posts using AI.

## How It Works

```
SessionStart → PostToolUse (logging) → SessionEnd → AI Summary → Markdown File
```

1. **SessionStart** - Initializes a session log when you start Claude Code
2. **PostToolUse** - Logs each tool usage (Write, Edit, Bash, Grep, etc.)
3. **SessionEnd** - Generates a developer diary post using AI when session ends

## Installation

1. Copy hooks to your Claude Code config:
```bash
mkdir -p ~/.claude/hooks/vibe-diary ~/.claude/vibe-diary/sessions ~/.claude/vibe-diary/posts
cp *.py ~/.claude/hooks/vibe-diary/
```

2. Add hooks to `~/.claude/settings.json`:
```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/vibe-diary/session_start.py"
      }]
    }],
    "PostToolUse": [{
      "matcher": "*",
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/vibe-diary/activity_logger.py"
      }]
    }],
    "SessionEnd": [{
      "hooks": [{
        "type": "command",
        "command": "python3 ~/.claude/hooks/vibe-diary/session_end.py"
      }]
    }]
  }
}
```

3. Set API key (Gemini or Anthropic):
```bash
export GEMINI_API_KEY="your-key"
# or
export ANTHROPIC_API_KEY="your-key"
```

4. Install dependencies:
```bash
pip install anthropic google-generativeai
```

## Output

Generated posts are saved to `~/.claude/vibe-diary/posts/` with frontmatter:

```markdown
---
title: "Developer Diary: my-project"
date: December 30, 2025
project: my-project
tags: [vibe-coding, claude-code]
generated: true
---

# What I Built Today
...
```

## Configuration

Edit `config.py` to customize:
- `LOGGED_TOOLS` - Which tools to track
- `SESSIONS_DIR` / `POSTS_DIR` - Output locations

## Requirements

- Python 3.8+
- `anthropic` or `google-generativeai` package
- Claude Code CLI

## License

MIT
