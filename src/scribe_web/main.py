from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from scribe_web.core.config import load_config
from scribe_web.core.constants import DEFAULT_CONFIG_PATH, PAYLOAD_FILENAME
from scribe_web.core.logging_setup import setup_logging
from scribe_web.core.paths import ensure_dirs, logs_root, repo_root, sessions_root
from scribe_web.core.payload_v1 import build_payload, build_step
from scribe_web.core.session import add_step, create_session


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

    payload = build_payload(session_name)
    payload_path = session_dir / PAYLOAD_FILENAME
    payload_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info("Smoke test payload written: %s", payload_path)
    return payload_path


def main() -> None:
    parser = argparse.ArgumentParser(description="SCRIBE_WEB CLI")
    parser.add_argument("--smoke", action="store_true", help="Run smoke test")
    parser.add_argument("--demo", action="store_true", help="Create demo session with sample steps")
    parser.add_argument("--panel", action="store_true", help="Run always-on-top control panel")
    args = parser.parse_args()

    if args.panel:
        config_path = repo_root() / DEFAULT_CONFIG_PATH
        config = load_config(config_path)
        from scribe_web.ui.panel import run_panel

        run_panel(config)
        return
    if args.smoke:
        payload_path = run_smoke_test()
        print("OK: smoke test complete")
        print(str(payload_path))
        return
    if args.demo:
        config_path = repo_root() / DEFAULT_CONFIG_PATH
        config = load_config(config_path)
        project_name = input("Podaj nazwę projektu (Enter = nowa_sesja): ").strip() or "nowa_sesja"
        ctx = create_session(project_name, config)
        add_step(
            ctx,
            build_step(
                1,
                "https://example.com/login",
                "Ekran logowania",
                "DEMO: tu wpisuję login i hasło.",
            ),
        )
        add_step(
            ctx,
            build_step(
                2,
                "https://example.com/dashboard",
                "Panel po zalogowaniu",
                "DEMO: tu pobieram dane i zapisuję je lokalnie.",
            ),
        )
        print("OK: demo session created")
        print(str(ctx.payload_path.resolve()))
        print(str(ctx.session_dir.resolve()))
        return

    print("No action specified. Use --smoke to run the smoke test.")
    sys.exit(1)


if __name__ == "__main__":
    main()
