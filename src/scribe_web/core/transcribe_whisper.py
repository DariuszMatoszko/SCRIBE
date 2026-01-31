from __future__ import annotations

from pathlib import Path

import whisper

_MODEL = None


def _get_model() -> whisper.Whisper:
    global _MODEL
    if _MODEL is None:
        _MODEL = whisper.load_model("base")
    return _MODEL


def transcribe_pl(in_wav: Path) -> str:
    model = _get_model()
    result = model.transcribe(str(in_wav), language="pl")
    return result["text"].strip()
