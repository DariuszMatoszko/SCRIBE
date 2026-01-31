from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class VoiceState:
    recording: bool = False
    step_id: int | None = None
    stream: Any = None
    buffer: list[Any] = field(default_factory=list)
    samplerate: int = 16000
    channels: int = 1


def start_recording(state: VoiceState) -> None:
    import sounddevice as sd

    state.buffer = []

    def callback(indata, _frames, _time, _status):
        state.buffer.append(indata.copy())

    state.stream = sd.InputStream(
        samplerate=state.samplerate,
        channels=state.channels,
        callback=callback,
    )
    state.stream.start()
    state.recording = True


def stop_and_save_wav(state: VoiceState, out_wav) -> None:
    import numpy as np
    import soundfile as sf

    if state.stream is not None:
        state.stream.stop()
        state.stream.close()
        state.stream = None

    if state.buffer:
        audio = np.concatenate(state.buffer, axis=0)
    else:
        audio = np.zeros((0, state.channels), dtype=np.float32)

    out_wav.parent.mkdir(parents=True, exist_ok=True)
    sf.write(out_wav, audio, state.samplerate)

    state.buffer = []
    state.recording = False
