from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scribe_web.core.paths import repo_root
from scribe_web.core.payload_v1 import build_payload
from scribe_web.core.utils import atomic_write_json, slugify


@dataclass
class SessionContext:
    project_name: str
    session_dir: Path
    payload_path: Path
    payload: dict


def _session_timestamp() -> str:
    return datetime.now(ZoneInfo("Europe/Warsaw")).strftime("%Y%m%d_%H%M%S")


def create_session(project_name: str, config: dict) -> SessionContext:
    sessions_root = repo_root() / config.get("sessions_root", "sessions")
    session_dir = sessions_root / f"{_session_timestamp()}__{slugify(project_name)}"

    (session_dir / "steps").mkdir(parents=True, exist_ok=True)
    (session_dir / "transcripts").mkdir(parents=True, exist_ok=True)
    (session_dir / "notes").mkdir(parents=True, exist_ok=True)
    (session_dir / "logs").mkdir(parents=True, exist_ok=True)

    payload = build_payload(project_name)
    payload_path = session_dir / "ai_payload.json"
    atomic_write_json(payload_path, payload)

    return SessionContext(
        project_name=project_name,
        session_dir=session_dir,
        payload_path=payload_path,
        payload=payload,
    )


def add_step(ctx: SessionContext, step: dict) -> None:
    ctx.payload.setdefault("steps", []).append(step)
    atomic_write_json(ctx.payload_path, ctx.payload)


def load_session(session_dir: Path) -> SessionContext:
    payload_path = session_dir / "ai_payload.json"
    payload = json.loads(payload_path.read_text(encoding="utf-8"))
    project_name = payload.get("session_meta", {}).get("project_name", "")
    return SessionContext(
        project_name=project_name,
        session_dir=session_dir,
        payload_path=payload_path,
        payload=payload,
    )
