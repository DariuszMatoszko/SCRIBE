from __future__ import annotations

import json
from pathlib import Path


def default_config() -> dict:
    return {
        "sessions_root": "sessions",
        "logs_root": "logs",
        "default_project_slug": "nowa_sesja",
        "timezone": "Europe/Warsaw",
        "privacy": {
            "mask_password_fields": True,
            "redact_query_params": True,
        },
    }


def load_config(path: Path) -> dict:
    config = default_config()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return config
    except json.JSONDecodeError:
        return config

    if isinstance(data, dict):
        config.update(data)
    return config
