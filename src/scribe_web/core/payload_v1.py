from __future__ import annotations

import platform
import sys

from scribe_web.core.utils import now_warsaw_iso


def build_payload(project_name: str) -> dict:
    return {
        "session_meta": {
            "project_name": project_name,
            "created_at": now_warsaw_iso(),
            "purpose": "automation_for_ai",
            "env": {
                "os": platform.system(),
                "python": sys.version.split()[0],
                "language": "pl-PL",
            },
        },
        "steps": [],
        "raw_logs": {},
    }


def build_step(step_id: int, url: str, title: str, note: str) -> dict:
    return {
        "id": step_id,
        "ts": now_warsaw_iso(),
        "url": url,
        "title": title,
        "assets": {"screenshot": "", "annotated": ""},
        "text": {
            "voice_transcript_raw": "",
            "voice_transcript_clean": "",
            "notes_clean": note,
        },
        "between_steps_summary": {"clicks": 0, "keys_summary": [], "navigations": 0},
        "probe": {"clicked_element": None, "network_summary": []},
        "privacy": {"paused": False, "redactions_applied": []},
    }
