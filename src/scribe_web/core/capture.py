from __future__ import annotations

from pathlib import Path

from mss import mss
from PIL import Image


def capture_fullscreen_png(out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with mss() as sct:
        monitor_index = 1 if len(sct.monitors) > 1 else 0
        monitor = sct.monitors[monitor_index]
        screenshot = sct.grab(monitor)
        image = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
        image.save(out_path, format="PNG")
