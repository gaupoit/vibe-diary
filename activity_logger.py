#!/usr/bin/env python3
"""Activity Logger Hook - Log tool usage during session"""
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent dir to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import SESSIONS_DIR, LOGGED_TOOLS


def extract_tool_summary(tool_name: str, tool_input: dict, tool_response: str) -> dict:
    """Extract relevant info based on tool type"""
    summary = {"tool": tool_name}

    if tool_name == "Write":
        summary["action"] = "created file"
        summary["file"] = tool_input.get("file_path", "")

    elif tool_name == "Edit":
        summary["action"] = "edited file"
        summary["file"] = tool_input.get("file_path", "")

    elif tool_name == "Bash":
        summary["action"] = "ran command"
        summary["command"] = tool_input.get("command", "")[:200]  # Truncate
        summary["description"] = tool_input.get("description", "")

    elif tool_name == "Grep":
        summary["action"] = "searched code"
        summary["pattern"] = tool_input.get("pattern", "")
        summary["path"] = tool_input.get("path", "")

    elif tool_name == "Glob":
        summary["action"] = "found files"
        summary["pattern"] = tool_input.get("pattern", "")

    elif tool_name in ("WebSearch", "WebFetch"):
        summary["action"] = "searched web" if tool_name == "WebSearch" else "fetched url"
        summary["query"] = tool_input.get("query", tool_input.get("url", ""))

    elif tool_name == "Task":
        summary["action"] = "launched agent"
        summary["description"] = tool_input.get("description", "")

    else:
        summary["action"] = "used tool"
        summary["input_keys"] = list(tool_input.keys())[:5]

    # Check for errors in response
    if tool_response and "error" in tool_response.lower()[:100]:
        summary["had_error"] = True

    return summary


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    tool_name = input_data.get("tool_name", "")

    # Skip tools we don't want to log
    if tool_name not in LOGGED_TOOLS:
        sys.exit(0)

    session_id = input_data.get("session_id", "unknown")
    tool_input = input_data.get("tool_input", {})
    tool_response = input_data.get("tool_response", "")

    # Find session file
    session_file = SESSIONS_DIR / f"{session_id}.jsonl"

    # Extract summary
    summary = extract_tool_summary(tool_name, tool_input, tool_response)
    summary["type"] = "activity"
    summary["timestamp"] = datetime.now().isoformat()

    # Append to session log
    with open(session_file, "a") as f:
        f.write(json.dumps(summary) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
