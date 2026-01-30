from __future__ import annotations

from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def sessions_root(config: dict) -> Path:
    return repo_root() / config.get("sessions_root", "sessions")


def logs_root(config: dict) -> Path:
    return repo_root() / config.get("logs_root", "logs")


def ensure_dirs(paths: list[Path]) -> None:
    for path in paths:
        path.mkdir(parents=True, exist_ok=True)
