from __future__ import annotations

from pathlib import Path

import sounddevice as sd
import soundfile as sf


def record_wav(
    out_wav: Path,
    seconds: int = 20,
    samplerate: int = 16000,
    channels: int = 1,
) -> None:
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    frames = int(seconds * samplerate)
    recording = sd.rec(frames, samplerate=samplerate, channels=channels, dtype="float32")
    sd.wait()
    sf.write(str(out_wav), recording, samplerate)
