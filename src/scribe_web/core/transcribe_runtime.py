from __future__ import annotations

from pathlib import Path

_WHISPER_MODEL = None


def transcribe_pl_optional(in_wav: Path) -> tuple[str, str]:
    try:
        import whisper
    except ModuleNotFoundError:
        return "", ""

    global _WHISPER_MODEL
    if _WHISPER_MODEL is None:
        _WHISPER_MODEL = whisper.load_model("base")

    result = _WHISPER_MODEL.transcribe(str(in_wav), language="pl")
    raw_text = (result.get("text") or "").strip()
    clean_text = raw_text
    return raw_text, clean_text
