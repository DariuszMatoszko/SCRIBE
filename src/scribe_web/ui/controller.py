from __future__ import annotations

from pathlib import Path

from scribe_web.core.capture import capture_fullscreen_png
from scribe_web.core.payload_v1 import build_step
from scribe_web.core.session import SessionContext, add_step, create_session
from scribe_web.core.logging_setup import setup_logging
from scribe_web.core.paths import ensure_dirs, logs_root
from scribe_web.core.utils import atomic_write_json
from scribe_web.ui.annotator import annotate_image


class Controller:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.ctx: SessionContext | None = None
        self.next_step_id = 1
        self.paused = False
        self.project_name: str | None = None
        self.last_action: str | None = None
        logs_dir = logs_root(config)
        ensure_dirs([logs_dir])
        self.logger = setup_logging(logs_dir / "scribe_web.log")

    def get_status(self) -> dict:
        return {
            "project_name": self.ctx.project_name if self.ctx else None,
            "steps": len(self.ctx.payload["steps"]) if self.ctx else 0,
            "paused": self.paused,
            "last_action": self.last_action,
        }

    def start_session(self, project_name: str) -> Path:
        self.ctx = create_session(project_name, self.config)
        self.next_step_id = 1
        self.paused = False
        self.project_name = project_name
        self.last_action = "S"
        self.logger.info("START session: %s", project_name)
        return self.ctx.session_dir

    def add_step_screenshot(self) -> None:
        if self.ctx is None:
            raise RuntimeError("Session has not been started yet")
        step_id = self.next_step_id
        screenshot_rel = f"steps/step_{step_id:03d}.png"
        screenshot_abs = self.ctx.session_dir / screenshot_rel
        capture_fullscreen_png(screenshot_abs)
        step = build_step(step_id, "", "", "")
        step["assets"]["screenshot"] = screenshot_rel
        step["privacy"]["paused"] = self.paused
        add_step(self.ctx, step)
        self.next_step_id += 1
        self.last_action = "K"
        self.logger.info(
            "ADD step: %s screenshot=%s paused=%s",
            step["id"],
            screenshot_rel,
            self.paused,
        )

    def annotate_last_step(self) -> bool:
        if self.ctx is None:
            self.logger.info("ANNOTATE step: ok=False steps=0")
            return False
        steps = self.ctx.payload.get("steps", [])
        if not steps:
            self.logger.info("ANNOTATE step: ok=False steps=0")
            return False
        step = steps[-1]
        screenshot_rel = step.get("assets", {}).get("screenshot") or ""
        if not screenshot_rel:
            self.logger.info("ANNOTATE step: ok=False screenshot=missing")
            return False
        input_path = self.ctx.session_dir / screenshot_rel
        output_rel = f"steps/step_{step['id']:03d}_annot.png"
        output_abs = self.ctx.session_dir / output_rel
        ok = annotate_image(input_path, output_abs)
        if ok:
            step["assets"]["annotated"] = output_rel
            atomic_write_json(self.ctx.payload_path, self.ctx.payload)
            self.last_action = "E"
            self.logger.info(
                "ANNOTATE step: ok=True step=%s output=%s",
                step["id"],
                output_rel,
            )
        else:
            self.logger.info("ANNOTATE step: ok=False step=%s", step["id"])
        return ok

    def toggle_pause(self) -> bool:
        self.paused = not self.paused
        self.last_action = "||"
        self.logger.info("PAUSE toggled: %s", self.paused)
        return self.paused

    def undo_last_step(self) -> bool:
        if self.ctx is None:
            self.logger.info("UNDO step: ok=False steps=0")
            return False
        steps = self.ctx.payload["steps"]
        if not steps:
            self.logger.info("UNDO step: ok=False steps=0")
            return False
        steps.pop()
        atomic_write_json(self.ctx.payload_path, self.ctx.payload)
        self.next_step_id = len(steps) + 1
        self.last_action = "↩"
        self.logger.info("UNDO step: ok=True steps=%s", len(steps))
        return True

    def end_session(self) -> Path | None:
        if self.ctx is None:
            return None
        session_dir = self.ctx.session_dir
        self.ctx = None
        self.project_name = None
        self.paused = False
        self.last_action = None
        return session_dir
