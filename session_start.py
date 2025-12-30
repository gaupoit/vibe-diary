#!/usr/bin/env python3
"""Session Start Hook - Initialize session log"""
import json
import sys
from datetime import datetime
from pathlib import Path

# Add parent dir to path for config import
sys.path.insert(0, str(Path(__file__).parent))
from config import SESSIONS_DIR


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    session_id = input_data.get("session_id", "unknown")
    cwd = input_data.get("cwd", "")
    transcript_path = input_data.get("transcript_path", "")

    # Extract project name from cwd
    project_name = Path(cwd).name if cwd else "unknown"

    # Create session log file
    session_file = SESSIONS_DIR / f"{session_id}.jsonl"

    # Write initial session metadata
    metadata = {
        "type": "session_start",
        "timestamp": datetime.now().isoformat(),
        "session_id": session_id,
        "project": project_name,
        "cwd": cwd,
        "transcript_path": transcript_path,
    }

    with open(session_file, "a") as f:
        f.write(json.dumps(metadata) + "\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
