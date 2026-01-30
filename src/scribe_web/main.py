from __future__ import annotations

import argparse
import json
import platform
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from scribe_web.core.config import load_config
from scribe_web.core.constants import DEFAULT_CONFIG_PATH, PAYLOAD_FILENAME
from scribe_web.core.logging_setup import setup_logging
from scribe_web.core.paths import ensure_dirs, logs_root, repo_root, sessions_root


def _build_payload(session_name: str, timezone: str) -> dict:
    now = datetime.now(ZoneInfo(timezone)).isoformat()
    return {
        "session_meta": {
            "project_name": session_name,
            "created_at": now,
            "purpose": "automation_for_ai",
            "env": {
                "os": platform.system(),
                "python": platform.python_version(),
                "language": "pl-PL",
            },
        },
        "steps": [],
        "raw_logs": {},
    }


def run_smoke_test() -> Path:
    config_path = repo_root() / DEFAULT_CONFIG_PATH
    config = load_config(config_path)

    sessions_dir = sessions_root(config)
    logs_dir = logs_root(config)
    ensure_dirs([sessions_dir, logs_dir])

    logger = setup_logging(logs_dir / "scribe_web.log")
    logger.info("Starting smoke test")

    session_name = "_smoke_test"
    session_dir = sessions_dir / session_name
    ensure_dirs([session_dir])

    payload = _build_payload(session_name, config.get("timezone", "Europe/Warsaw"))
    payload_path = session_dir / PAYLOAD_FILENAME
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info("Smoke test payload written: %s", payload_path)
    return payload_path


def main() -> None:
    parser = argparse.ArgumentParser(description="SCRIBE_WEB CLI")
    parser.add_argument("--smoke", action="store_true", help="Run smoke test")
    args = parser.parse_args()

    if args.smoke:
        payload_path = run_smoke_test()
        print("OK: smoke test complete")
        print(str(payload_path))
        return

    print("No action specified. Use --smoke to run the smoke test.")
    sys.exit(1)


if __name__ == "__main__":
    main()
