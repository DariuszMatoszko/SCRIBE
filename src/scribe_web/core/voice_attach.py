from __future__ import annotations

from pathlib import Path

from scribe_web.core.session import SessionContext
from scribe_web.core.utils import atomic_write_json


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def record_and_attach_to_last_step(ctx: SessionContext, seconds: int = 20) -> dict:
    from scribe_web.core.audio_recorder import record_wav
    from scribe_web.core.transcribe_whisper import transcribe_pl

    steps = ctx.payload.get("steps", [])
    if not steps:
        raise RuntimeError("Brak kroku. Najpierw zrób K.")
    step = steps[-1]
    step_id = step["id"]

    wav_rel = f"transcripts/step_{step_id:03d}.wav"
    raw_rel = f"transcripts/step_{step_id:03d}_raw.txt"
    clean_rel = f"transcripts/step_{step_id:03d}_clean.txt"

    wav_abs = ctx.session_dir / wav_rel
    record_wav(wav_abs, seconds=seconds)

    raw_text = transcribe_pl(wav_abs)
    raw_abs = ctx.session_dir / raw_rel
    _write_text(raw_abs, raw_text)

    clean_text = raw_text
    print("--- TRANSKRYPCJA RAW ---")
    print(raw_text)
    print("--- KONIEC RAW ---")
    user_text = input("Wklej poprawiony tekst (Enter = zostaw bez zmian): ").strip()
    if user_text:
        clean_text = user_text

    clean_abs = ctx.session_dir / clean_rel
    _write_text(clean_abs, clean_text)

    step_text = step.setdefault("text", {})
    step_text["voice_transcript_raw"] = raw_rel
    step_text["voice_transcript_clean"] = clean_rel

    atomic_write_json(ctx.payload_path, ctx.payload)

    return {"wav": wav_rel, "raw": raw_rel, "clean": clean_rel}
