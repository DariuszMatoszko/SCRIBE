from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
import shutil

from scribe_web.core.capture import capture_fullscreen_png
from scribe_web.core.payload_v1 import build_step
from scribe_web.core.session import SessionContext, add_step, create_session
from scribe_web.core.logging_setup import setup_logging
from scribe_web.core.paths import ensure_dirs, logs_root
from scribe_web.core.utils import atomic_write_json
from scribe_web.core.voice_attach import record_and_attach_to_last_step
from scribe_web.core.transcribe_runtime import transcribe_pl_optional
from scribe_web.core.voice_runtime import VoiceState, start_recording, stop_and_save_wav
from scribe_web.ui.annotator import annotate_freehand_blocking


class Controller:
    def __init__(self, config: dict) -> None:
        self.config = config
        self.ctx: SessionContext | None = None
        self.next_step_id = 1
        self.paused = False
        self.project_name: str | None = None
        self.last_action: str | None = None
        self.voice_state = VoiceState()
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
        rel = f"steps/step_{step_id:03d}.png"
        abs_path = self.ctx.session_dir / rel
        capture_fullscreen_png(abs_path)
        step = build_step(step_id, url="", title="", note="")
        step["assets"]["screenshot"] = rel
        step["privacy"]["paused"] = self.paused
        add_step(self.ctx, step)
        self.next_step_id += 1
        self.last_action = "K"
        self.logger.info(
            "ADD step: %s screenshot=%s paused=%s",
            step["id"],
            rel,
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
        screenshot_abs = self.ctx.session_dir / screenshot_rel
        orig_rel = f"steps/step_{step['id']:03d}_orig.png"
        orig_abs = self.ctx.session_dir / orig_rel
        if not orig_abs.exists():
            shutil.copy2(screenshot_abs, orig_abs)
        ok = annotate_freehand_blocking(orig_abs, screenshot_abs)
        if ok:
            step["assets"]["annotated"] = screenshot_rel
            atomic_write_json(self.ctx.payload_path, self.ctx.payload)
            self.last_action = "E"
            self.logger.info(
                "ANNOTATE step: ok=True step=%s output=%s",
                step["id"],
                screenshot_rel,
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

    def record_voice_last_step(self, seconds: int = 20) -> dict:
        if self.ctx is None:
            raise RuntimeError("Session has not been started yet")
        result = record_and_attach_to_last_step(self.ctx, seconds=seconds)
        self.last_action = "G"
        self.logger.info(
            "VOICE step: step=%s wav=%s",
            self.ctx.payload["steps"][-1]["id"],
            result["wav"],
        )
        return result

    def toggle_voice_last_step(self) -> dict:
        if self.ctx is None:
            raise RuntimeError("Brak kroku. Najpierw zrób K.")
        steps = self.ctx.payload.get("steps", [])
        if not steps:
            raise RuntimeError("Brak kroku. Najpierw zrób K.")

        step_id = steps[-1]["id"]
        if not self.voice_state.recording:
            self.voice_state.step_id = step_id
            start_recording(self.voice_state)
            self.last_action = "G"
            self.logger.info("VOICE start: step=%s", step_id)
            return {"recording": True, "step_id": step_id}

        target_step_id = self.voice_state.step_id or step_id
        step = next(
            (item for item in steps if item.get("id") == target_step_id),
            None,
        )
        if step is None:
            raise RuntimeError("Brak kroku. Najpierw zrób K.")

        wav_rel = f"transcripts/step_{target_step_id:03d}.wav"
        raw_rel = f"transcripts/step_{target_step_id:03d}_raw.txt"
        clean_rel = f"transcripts/step_{target_step_id:03d}_clean.txt"

        out_wav_abs = self.ctx.session_dir / wav_rel
        stop_and_save_wav(self.voice_state, out_wav_abs)

        raw_text, clean_text = transcribe_pl_optional(out_wav_abs)
        raw_abs = self.ctx.session_dir / raw_rel
        raw_abs.parent.mkdir(parents=True, exist_ok=True)
        raw_abs.write_text(raw_text, encoding="utf-8")

        clean_abs = self.ctx.session_dir / clean_rel
        clean_abs.parent.mkdir(parents=True, exist_ok=True)
        clean_abs.write_text(clean_text, encoding="utf-8")

        step_text = step.setdefault("text", {})
        step_text["voice_transcript_raw"] = raw_rel
        step_text["voice_transcript_clean"] = clean_rel
        atomic_write_json(self.ctx.payload_path, self.ctx.payload)

        self.voice_state.step_id = None
        self.last_action = "G"
        self.logger.info(
            "VOICE stop: step=%s wav=%s transcribed=%s",
            target_step_id,
            wav_rel,
            bool(raw_text or clean_text),
        )
        return {
            "recording": False,
            "step_id": target_step_id,
            "wav": wav_rel,
            "raw": raw_rel,
            "clean": clean_rel,
            "transcribed": bool(raw_text or clean_text),
        }

    def add_step_screenshot_and_edit_and_voice(self, seconds: int = 20) -> bool:
        self.add_step_screenshot()
        ok = self.annotate_last_step()
        if not ok:
            return False
        self.record_voice_last_step(seconds=seconds)
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

    def clean_empty_sessions(self) -> dict:
        """
        Przenosi puste sesje (steps==[]) do sessions/_trash.
        Zwraca podsumowanie: {"moved": int, "trash_dir": str}
        """
        sessions_root = Path(self.config.get("sessions_root", "sessions"))
        trash_dir = sessions_root / "_trash"
        trash_dir.mkdir(parents=True, exist_ok=True)

        moved = 0
        for p in sessions_root.iterdir():
            if not p.is_dir():
                continue
            name = p.name
            if name in ("_trash", "_smoke_test"):
                continue
            payload = p / "ai_payload.json"
            if not payload.exists():
                continue
            try:
                data = json.loads(payload.read_text(encoding="utf-8"))
            except Exception:
                continue
            steps = data.get("steps", None)
            if steps is None:
                continue
            if len(steps) != 0:
                continue

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            dest = trash_dir / f"{name}__{ts}"
            i = 1
            while dest.exists():
                dest = trash_dir / f"{name}__{ts}_{i}"
                i += 1
            p.rename(dest)
            moved += 1

        self.last_action = "C"
        self.logger.info("CLEAN moved=%s trash=%s", moved, trash_dir)
        return {"moved": moved, "trash_dir": str(trash_dir)}
