from __future__ import annotations

import logging
from pathlib import Path

from scribe_web.core.payload_v1 import build_step
from scribe_web.core.session import SessionContext, add_step, create_session
from scribe_web.core.utils import atomic_write_json


class Controller:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.ctx: SessionContext | None = None
        self.next_step_id = 1
        self.paused = False
        self.project_name: str | None = None
        self.logger = logging.getLogger(__name__)

    def get_status(self) -> dict:
        steps = 0
        if self.ctx is not None:
            steps = len(self.ctx.payload.get("steps", []))
        return {
            "project_name": self.project_name,
            "steps": steps,
            "paused": self.paused if self.ctx is not None else False,
        }

    def start_session(self, project_name: str) -> Path:
        self.ctx = create_session(project_name, self.config)
        self.next_step_id = 1
        self.paused = False
        self.project_name = project_name
        self.logger.info("START session: %s", project_name)
        return self.ctx.session_dir

    def add_step_stub(self) -> None:
        if self.ctx is None:
            raise RuntimeError("Session has not been started yet")
        step = build_step(self.next_step_id, "", "", "")
        step["privacy"]["paused"] = self.paused
        add_step(self.ctx, step)
        self.next_step_id += 1
        self.logger.info("ADD step: %s paused=%s", step["id"], self.paused)

    def toggle_pause(self) -> bool:
        self.paused = not self.paused
        self.logger.info("PAUSE toggled: %s", self.paused)
        return self.paused

    def undo_last_step(self) -> bool:
        if self.ctx is None:
            self.logger.info("UNDO step: ok=False steps=0")
            return False
        steps = self.ctx.payload.get("steps", [])
        if not steps:
            self.logger.info("UNDO step: ok=False steps=0")
            return False
        steps.pop()
        atomic_write_json(self.ctx.payload_path, self.ctx.payload)
        self.next_step_id = len(steps) + 1
        self.logger.info("UNDO step: ok=True steps=%s", len(steps))
        return True

    def end_session(self) -> Path | None:
        if self.ctx is None:
            return None
        session_dir = self.ctx.session_dir
        self.ctx = None
        self.project_name = None
        return session_dir
